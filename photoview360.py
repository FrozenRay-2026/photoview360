from qgis.PyQt.QtCore import (
    QSettings,
    QTranslator,
    QCoreApplication,
    Qt
)

from qgis.PyQt.QtGui import (
    QIcon,
    QColor
)

from qgis.PyQt.QtWidgets import QAction

from qgis.gui import (
    QgsMapToolIdentify,
    QgsHighlight
)

from qgis.core import QgsVectorLayer

from .resources import *
from .photoview360_dialog import PhotoView360Dialog

import os
import time
import socket
import socketserver
import http.server
import threading


class PhotoView360:

    def __init__(self, iface):
        self.iface = iface

        self.httpd = None
        self.server_port = None
        self.server_folder = None

        self.plugin_dir = os.path.dirname(__file__)
        locale = QSettings().value('locale/userLocale')[0:2]
        locale_path = os.path.join(
            self.plugin_dir, 'i18n',
            'PhotoView360_{}.qm'.format(locale)
        )
        if os.path.exists(locale_path):
            self.translator = QTranslator()
            self.translator.load(locale_path)
            QCoreApplication.installTranslator(self.translator)

        self.actions = []
        self.menu = self.tr(u'&PhotoView360')
        self.first_start = None

        self.photo_layer = None
        self.image_field = None
        self.current_highlight = None

        self.click_tool = PhotoClickTool(self.iface.mapCanvas(), self)
        self.iface.mapCanvas().mapToolSet.connect(self.on_map_tool_changed)

    def tr(self, message):
        return QCoreApplication.translate('PhotoView360', message)

    def add_action(self, icon_path, text, callback, enabled_flag=True,
                   add_to_menu=True, add_to_toolbar=True,
                   status_tip=None, whats_this=None, parent=None):
        icon = QIcon(icon_path)
        action = QAction(icon, text, parent)
        action.triggered.connect(callback)
        action.setEnabled(enabled_flag)
        if status_tip is not None:
            action.setStatusTip(status_tip)
        if whats_this is not None:
            action.setWhatsThis(whats_this)
        if add_to_toolbar:
            self.iface.addToolBarIcon(action)
        if add_to_menu:
            self.iface.addPluginToMenu(self.menu, action)
        self.actions.append(action)
        return action

    def initGui(self):
        icon_path = ':/plugins/photoview360/icon.png'
        self.add_action(
            icon_path,
            text=self.tr(u'PhotoView360'),
            callback=self.run,
            parent=self.iface.mainWindow()
        )
        self.first_start = True

    def unload(self):
        if self.httpd:
            self.httpd.shutdown()
            self.httpd.server_close()
            self.httpd = None
        for action in self.actions:
            self.iface.removePluginMenu(self.tr(u'&PhotoView360'), action)
            self.iface.removeToolBarIcon(action)
        try:
            self.iface.mapCanvas().mapToolSet.disconnect(self.on_map_tool_changed)
        except TypeError:
            pass
        self.clear_highlight()

    def update_fields(self):
        layer = self.dlg.cmbLayer.currentLayer()
        if not layer or not isinstance(layer, QgsVectorLayer):
            return
        self.dlg.cmbField.setLayer(layer)
        self.dlg.cmbFileNameField.setLayer(layer)

    def activate_click_tool(self):
        self.photo_layer = self.dlg.cmbLayer.currentLayer()

        if self.dlg.mode == 'fullpath':
            self.image_field = self.dlg.cmbField.currentText()
        else:
            self.image_field = self.dlg.cmbFileNameField.currentText()

        if self.dlg.btnSelectLocation.isChecked():
            self.iface.mapCanvas().setMapTool(self.click_tool)
        else:
            self.iface.mapCanvas().unsetMapTool(self.click_tool)

    def on_map_tool_changed(self, new_tool, old_tool):
        if new_tool is not self.click_tool:
            if hasattr(self, 'dlg'):
                self.dlg.btnSelectLocation.setChecked(False)

    def on_dialog_closed(self):
        self.iface.mapCanvas().unsetMapTool(self.click_tool)
        self.clear_highlight()
        self.dlg.btnSelectLocation.setChecked(False)

    def run(self):
        if self.first_start:
            self.first_start = False

            self.dlg = PhotoView360Dialog(self.iface.mainWindow())
            self.dlg.setWindowFlags(
                Qt.Window |
                Qt.WindowCloseButtonHint |
                Qt.WindowMinimizeButtonHint
            )

            self.dlg.cmbLayer.layerChanged.connect(self.update_fields)
            self.dlg.btnSelectLocation.setCheckable(True)
            self.dlg.btnSelectLocation.clicked.connect(self.activate_click_tool)
            self.dlg.finished.connect(self.on_dialog_closed)

            self.update_fields()

        self.clear_highlight()
        self.dlg.show()
        self.dlg.raise_()

    def show_viewer(self, feature):
        # ---------- パス解決 ----------
        if self.dlg.mode == 'fullpath':
            # ① 属性値がそのままフルパス
            image_path = feature[self.image_field]
            if not image_path or not os.path.isfile(image_path):
                self.iface.messageBar().pushWarning(
                    "PhotoView360", f"画像が見つかりません\n{image_path}"
                )
                return

        else:
            # ② ファイル名 + フォルダから検索
            filename_val = feature[self.image_field]
            base_folder  = self.dlg.image_folder
            include_sub  = self.dlg.include_subfolders

            if not filename_val:
                self.iface.messageBar().pushWarning(
                    "PhotoView360", "ファイル名フィールドが空です"
                )
                return
            if not base_folder or not os.path.isdir(base_folder):
                self.iface.messageBar().pushWarning(
                    "PhotoView360", f"フォルダが見つかりません\n{base_folder}"
                )
                return

            image_path = self._find_image(filename_val, base_folder, include_sub)
            if image_path is None:
                self.iface.messageBar().pushWarning(
                    "PhotoView360",
                    f"画像が見つかりません: {filename_val}"
                    + ("\n（サブフォルダ含む）" if include_sub else "")
                )
                return

        # ---------- 以下は既存コードと同じ ----------
        self.highlight_feature(feature)

        folder   = os.path.dirname(image_path)
        filename = os.path.basename(image_path)
        html_filename = "viewer.html"
        html_path = os.path.join(folder, html_filename)

        port = self.start_image_server(folder)
        if port is None:
            self.iface.messageBar().pushWarning(
                "PhotoView360", "サーバーの起動に失敗しました"
            )
            return

        image_url  = f"http://localhost:{port}/{filename}?t={int(time.time())}"
        viewer_url = f"http://localhost:{port}/{html_filename}"

        html = f"""<!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <title>PhotoView360</title>
        <link rel="icon" href="data:,">
        <script src="https://aframe.io/releases/1.7.0/aframe.min.js"></script>
    </head>
    <body style="margin:0; overflow:hidden;">
    <a-scene id="scene">
        <a-assets>
            <img id="pano" src="{image_url}" crossorigin="anonymous">
        </a-assets>
        <a-sky src="#pano"></a-sky>
        <a-camera id="cam" look-controls="reverseMouseDrag: false"></a-camera>
    </a-scene>
    <script>
    const scene = document.querySelector('#scene');
    scene.addEventListener('loaded', function () {{
        const cam = document.querySelector('#cam');
        scene.canvas.addEventListener('wheel', function(e) {{
        e.preventDefault();
        const fovNow = cam.getAttribute('camera').fov;
        const delta  = e.deltaY * 0.05;
        const fovNew = Math.min(120, Math.max(20, fovNow + delta));
        const rect = scene.canvas.getBoundingClientRect();
        const nx =  ((e.clientX - rect.left) / rect.width  - 0.5) * 2;
        const ny = -((e.clientY - rect.top)  / rect.height - 0.5) * 2;
        const shiftScale = (fovNow - fovNew) * 0.5;
        const rot = cam.getAttribute('rotation');
        cam.setAttribute('rotation', {{
            x: rot.x + ny * shiftScale,
            y: rot.y + nx * shiftScale,
            z: rot.z
        }});
        cam.setAttribute('camera', 'fov', fovNew);
        }}, {{ passive: false }});
    }});
    </script>
    </body>
    </html>"""

        with open(html_path, "w", encoding="utf-8") as f:
            f.write(html)

        import webbrowser
        webbrowser.open(viewer_url)

    # ──────────────────────────────────────────
    # ローカルHTTPサーバー（ポート競合・起動タイミング問題を修正）
    # ──────────────────────────────────────────
    def start_image_server(self, folder):
        # 同じフォルダなら既存サーバーを再利用
        if self.httpd is not None and self.server_folder == folder:
            return self.server_port

        # 既存サーバーをバックグラウンドで終了（UIスレッドのブロック回避）
        if self.httpd:
            old = self.httpd
            threading.Thread(
                target=lambda: (old.shutdown(), old.server_close()),
                daemon=True
            ).start()
            self.httpd = None

        class Handler(http.server.SimpleHTTPRequestHandler):
            def __init__(self, *args, **kwargs):
                super().__init__(*args, directory=folder, **kwargs)
            def end_headers(self):
                self.send_header("Access-Control-Allow-Origin", "*")
                self.send_header("Cache-Control", "no-store")
                super().end_headers()
            def log_message(self, format, *args):
                pass  # QGISのログを汚さない

        class ReuseTCPServer(socketserver.TCPServer):
            allow_reuse_address = True

        try:
            # port=0 でOSが空きポートを直接割り当て（競合ゼロ）
            server = ReuseTCPServer(("localhost", 0), Handler)
        except OSError as e:
            self.iface.messageBar().pushWarning(
                "PhotoView360", f"サーバー作成に失敗: {e}"
            )
            return None

        port = server.server_address[1]

        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()

        # サーバーが実際に接続を受け付けるまで待つ（最大1秒）
        for _ in range(20):
            try:
                s = socket.create_connection(("localhost", port), timeout=0.05)
                s.close()
                break
            except OSError:
                time.sleep(0.05)
        else:
            # 20回試してもつながらなければ失敗
            server.shutdown()
            server.server_close()
            return None

        self.httpd = server
        self.server_port = port
        self.server_folder = folder
        return port

    # ──────────────────────────────────────────
    # ハイライト管理
    # ──────────────────────────────────────────
    def clear_highlight(self):
        if self.current_highlight is not None:
            self.current_highlight.hide()
            self.current_highlight = None

    def highlight_feature(self, feature):
        self.clear_highlight()
        if not self.photo_layer:
            return
        self.current_highlight = QgsHighlight(
            self.iface.mapCanvas(),
            feature,
            self.photo_layer
        )
        self.current_highlight.setColor(QColor(255, 0, 0))
        self.current_highlight.setFillColor(QColor(255, 0, 0, 160))
        self.current_highlight.setWidth(6)
        self.current_highlight.show()

    def _find_image(self, filename, base_folder, include_sub):
        """
        filename    : 属性から取得したファイル名（例: "IMG_001.jpg"）
        base_folder : 検索起点フォルダ
        include_sub : True なら os.walk でサブフォルダも探す
        戻り値      : 見つかったフルパス or None
        """
        if include_sub:
            for root, _dirs, files in os.walk(base_folder):
                if filename in files:
                    return os.path.join(root, filename)
        else:
            candidate = os.path.join(base_folder, filename)
            if os.path.isfile(candidate):
                return candidate
        return None


class PhotoClickTool(QgsMapToolIdentify):

    def __init__(self, canvas, plugin):
        super().__init__(canvas)
        self.canvas = canvas
        self.plugin = plugin

    def canvasReleaseEvent(self, event):
        results = self.identify(
            event.x(),
            event.y(),
            [self.plugin.photo_layer],
            QgsMapToolIdentify.TopDownAll
        )

        if not results:
            self.plugin.iface.messageBar().pushInfo(
                "PhotoView360", "フィーチャが見つかりません"
            )
            return

        feature = results[0].mFeature
        self.plugin.show_viewer(feature)