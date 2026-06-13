# -*- coding: utf-8 -*-

import os

from qgis.PyQt import uic
from qgis.PyQt import QtWidgets

FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'photoview360_dialog_base.ui'))


class PhotoView360Dialog(QtWidgets.QDialog, FORM_CLASS):
    def __init__(self, parent=None):
        super(PhotoView360Dialog, self).__init__(parent)
        self.setupUi(self)
        self._connect_signals()
        self._update_mode_widgets()

    # ──────────────────────────────────────────
    # シグナル接続
    # ──────────────────────────────────────────
    def _connect_signals(self):
        self.rdoFullPath.toggled.connect(self._update_mode_widgets)
        self.btnBrowseFolder.clicked.connect(self._browse_folder)

    # ──────────────────────────────────────────
    # モードに応じてウィジェットの有効/無効を切り替え
    # ──────────────────────────────────────────
    def _update_mode_widgets(self):
        is_full = self.rdoFullPath.isChecked()

        # ① フルパスモード用
        self.lblField.setEnabled(is_full)
        self.cmbField.setEnabled(is_full)

        # ② ファイル名モード用
        self.lblFileNameField.setEnabled(not is_full)
        self.cmbFileNameField.setEnabled(not is_full)
        self.lblFolder.setEnabled(not is_full)
        self.txtFolder.setEnabled(not is_full)
        self.btnBrowseFolder.setEnabled(not is_full)
        self.chkSubFolder.setEnabled(not is_full)

    # ──────────────────────────────────────────
    # フォルダ選択ダイアログ
    # ──────────────────────────────────────────
    def _browse_folder(self):
        folder = QtWidgets.QFileDialog.getExistingDirectory(
            self,
            "画像フォルダを選択",
            self.txtFolder.text() or os.path.expanduser("~")
        )
        if folder:
            self.txtFolder.setText(folder)

    # ──────────────────────────────────────────
    # 外部から参照するプロパティ
    # ──────────────────────────────────────────
    @property
    def mode(self):
        """'fullpath' または 'filename' を返す"""
        return 'fullpath' if self.rdoFullPath.isChecked() else 'filename'

    @property
    def image_folder(self):
        """② モード時の画像フォルダパス"""
        return self.txtFolder.text().strip()

    @property
    def include_subfolders(self):
        """② モード時のサブフォルダ検索フラグ"""
        return self.chkSubFolder.isChecked()
