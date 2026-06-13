# -*- coding: utf-8 -*-

import os
import webbrowser

from qgis.PyQt.QtCore import Qt
from qgis.PyQt.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QRadioButton, QCheckBox,
    QLineEdit, QGroupBox, QSizePolicy,
    QFileDialog, QFrame
)
from qgis.gui import QgsMapLayerComboBox, QgsFieldComboBox
from qgis.core import QgsMapLayerProxyModel


# ──────────────────────────────────────────
# テキスト定義（日本語 / 英語）
# ──────────────────────────────────────────
_TEXTS = {
    'ja': {
        'title':          'PhotoView360',
        'lang_btn':       'English',          # 「切り替え先」の言語名を表示
        'photo_layer':    'フォトレイヤー',
        'path_method':    '画像パスの指定方法',
        'rdo_full':       '① 属性フィールドでフルパスを指定',
        'lbl_full_field': 'フルパス フィールド',
        'rdo_file':       '② 属性フィールドでファイル名を指定',
        'lbl_file_field': 'ファイル名 フィールド',
        'lbl_folder':     '画像フォルダ',
        'folder_ph':      'フォルダを選択...',
        'browse':         '...',
        'subfolder':      'サブフォルダを含む',
        'select_loc':     '撮影地点を選択',
        'folder_dlg':     '画像フォルダを選択',
        'help_btn':       'ヘルプ',
    },
    'en': {
        'title':          'PhotoView360',
        'lang_btn':       '日本語',
        'photo_layer':    'Photo Layer',
        'path_method':    'Image Path Method',
        'rdo_full':       '① Specify full path via attribute field',
        'lbl_full_field': 'Full Path Field',
        'rdo_file':       '② Specify filename via attribute field',
        'lbl_file_field': 'File Name Field',
        'lbl_folder':     'Image Folder',
        'folder_ph':      'Select folder...',
        'browse':         '...',
        'subfolder':      'Include subfolders',
        'select_loc':     'Select photo location',
        'folder_dlg':     'Select Image Folder',
        'help_btn':       'Help',
    },
}


class PhotoView360Dialog(QDialog):

    _ITEM_SPACING = 4
    _GROUP_SPACING = 10

    def __init__(self, parent=None):
        super().__init__(parent)
        self._lang = 'ja'          # 初期言語
        self.setMinimumWidth(280)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)

        self._build_ui()
        self._connect_signals()
        self._apply_texts()
        self._update_mode_widgets()

    # ──────────────────────────────────────────
    # UI構築（テキストはダミー、_apply_texts で後付け）
    # ──────────────────────────────────────────
    def _build_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(12, 12, 12, 12)
        root.setSpacing(self._GROUP_SPACING)

        # ---- 言語切替ボタン（右揃え） ----
        lang_row = QHBoxLayout()
        lang_row.addStretch()
        self.btnLang = QPushButton()
        self.btnLang.setFixedWidth(70)
        lang_row.addWidget(self.btnLang)
        root.addLayout(lang_row)

        # ---- Photo Layer ----
        self.lblPhotoLayer = self._make_label("")
        root.addWidget(self.lblPhotoLayer)
        self.cmbLayer = QgsMapLayerComboBox()
        self.cmbLayer.setFilters(QgsMapLayerProxyModel.VectorLayer)
        root.addWidget(self.cmbLayer)

        # ---- モード選択グループ ----
        self.grpMode = QGroupBox()
        self.grpMode.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        grp_layout = QVBoxLayout(self.grpMode)
        grp_layout.setContentsMargins(10, 10, 10, 10)
        grp_layout.setSpacing(self._GROUP_SPACING)

        # ① ラジオ
        self.rdoFullPath = QRadioButton()
        self.rdoFullPath.setChecked(True)
        grp_layout.addWidget(self.rdoFullPath)

        # ① フィールド（インデント付きフレーム）
        self._frame_full = self._make_indent_frame()
        fl = QVBoxLayout(self._frame_full)
        fl.setContentsMargins(0, 0, 0, 0)
        fl.setSpacing(self._ITEM_SPACING)
        self.lblFullField = self._make_label("")
        fl.addWidget(self.lblFullField)
        self.cmbField = QgsFieldComboBox()
        fl.addWidget(self.cmbField)
        grp_layout.addWidget(self._frame_full)

        # セパレーター
        grp_layout.addWidget(self._make_separator())

        # ② ラジオ
        self.rdoFileName = QRadioButton()
        grp_layout.addWidget(self.rdoFileName)

        # ② フィールド＋フォルダ（インデント付きフレーム）
        self._frame_file = self._make_indent_frame()
        ffl = QVBoxLayout(self._frame_file)
        ffl.setContentsMargins(0, 0, 0, 0)
        ffl.setSpacing(self._ITEM_SPACING)

        self.lblFileNameField = self._make_label("")
        ffl.addWidget(self.lblFileNameField)
        self.cmbFileNameField = QgsFieldComboBox()
        ffl.addWidget(self.cmbFileNameField)

        ffl.addSpacing(4)
        self.lblFolder = self._make_label("")
        ffl.addWidget(self.lblFolder)

        folder_row = QHBoxLayout()
        folder_row.setSpacing(4)
        self.txtFolder = QLineEdit()
        folder_row.addWidget(self.txtFolder)
        self.btnBrowseFolder = QPushButton()
        self.btnBrowseFolder.setFixedWidth(30)
        folder_row.addWidget(self.btnBrowseFolder)
        ffl.addLayout(folder_row)

        ffl.addSpacing(2)
        self.chkSubFolder = QCheckBox()
        ffl.addWidget(self.chkSubFolder)

        grp_layout.addWidget(self._frame_file)
        root.addWidget(self.grpMode)

        # ---- Select Location ボタン ----
        self.btnSelectLocation = QPushButton()
        self.btnSelectLocation.setCheckable(True)
        root.addWidget(self.btnSelectLocation)

        # ---- Help ボタン ----
        self.btnHelp = QPushButton()
        root.addWidget(self.btnHelp)

    # ──────────────────────────────────────────
    # テキスト適用
    # ──────────────────────────────────────────
    def _apply_texts(self):
        t = _TEXTS[self._lang]
        self.setWindowTitle(t['title'])
        self.btnLang.setText(t['lang_btn'])
        self.lblPhotoLayer.setText(t['photo_layer'])
        self.grpMode.setTitle(t['path_method'])
        self.rdoFullPath.setText(t['rdo_full'])
        self.lblFullField.setText(t['lbl_full_field'])
        self.rdoFileName.setText(t['rdo_file'])
        self.lblFileNameField.setText(t['lbl_file_field'])
        self.lblFolder.setText(t['lbl_folder'])
        self.txtFolder.setPlaceholderText(t['folder_ph'])
        self.btnBrowseFolder.setText(t['browse'])
        self.chkSubFolder.setText(t['subfolder'])
        self.btnSelectLocation.setText(t['select_loc'])
        self.btnHelp.setText(t['help_btn'])

    # ──────────────────────────────────────────
    # 言語切替
    # ──────────────────────────────────────────
    def _toggle_language(self):
        self._lang = 'en' if self._lang == 'ja' else 'ja'
        self._apply_texts()

    # ──────────────────────────────────────────
    # ヘルパー
    # ──────────────────────────────────────────
    def _make_label(self, text):
        lbl = QLabel(text)
        lbl.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        return lbl

    def _make_indent_frame(self):
        frame = QFrame()
        frame.setContentsMargins(16, 0, 0, 0)
        frame.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        return frame

    def _make_separator(self):
        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setFrameShadow(QFrame.Sunken)
        return line

    # ──────────────────────────────────────────
    # シグナル接続
    # ──────────────────────────────────────────
    def _connect_signals(self):
        self.rdoFullPath.toggled.connect(self._update_mode_widgets)
        self.btnBrowseFolder.clicked.connect(self._browse_folder)
        self.btnLang.clicked.connect(self._toggle_language)
        self.btnHelp.clicked.connect(self._open_help)

    # ──────────────────────────────────────────
    # モード切替
    # ──────────────────────────────────────────
    def _update_mode_widgets(self):
        is_full = self.rdoFullPath.isChecked()
        self._frame_full.setEnabled(is_full)
        self._frame_file.setEnabled(not is_full)

        # モード変更時に select location を自動OFF
        self.btnSelectLocation.setChecked(False)
        self.btnSelectLocation.clicked.emit(False)

    # ──────────────────────────────────────────
    # フォルダ選択
    # ──────────────────────────────────────────
    def _browse_folder(self):
        folder = QFileDialog.getExistingDirectory(
            self,
            _TEXTS[self._lang]['folder_dlg'],
            self.txtFolder.text() or os.path.expanduser("~")
        )
        if folder:
            self.txtFolder.setText(folder)

    # ──────────────────────────────────────────
    # 外部参照プロパティ
    # ──────────────────────────────────────────
    @property
    def mode(self):
        return 'fullpath' if self.rdoFullPath.isChecked() else 'filename'

    @property
    def image_folder(self):
        return self.txtFolder.text().strip()

    @property
    
    def include_subfolders(self):
        return self.chkSubFolder.isChecked()
    
    # ──────────────────────────────────────────
    # ヘルプ
    # ──────────────────────────────────────────
    def _open_help(self):
        plugin_dir = os.path.dirname(os.path.abspath(__file__))
        help_file = os.path.join(plugin_dir, "README.html")

        if os.path.exists(help_file):
            webbrowser.open("file://" + help_file.replace("\\", "/"))