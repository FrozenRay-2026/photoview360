from PyQt5.QtWidgets import QDialog, QVBoxLayout
from PyQt5.QtWebEngineWidgets import QWebEngineView

class ViewerDialog(QDialog):

    def __init__(self, html):
        super().__init__()

        self.resize(1200, 800)

        layout = QVBoxLayout()

        self.web = QWebEngineView()
        self.web.setHtml(html)

        layout.addWidget(self.web)

        self.setLayout(layout)