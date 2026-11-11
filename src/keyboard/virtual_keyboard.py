from PySide6.QtWidgets import QWidget, QGridLayout, QPushButton, QVBoxLayout
from PySide6.QtCore import Qt
from .key_mapping import SPECIAL

class VirtualKeyboard(QWidget):
    def __init__(self, on_key):
        super().__init__(None, Qt.WindowType.Tool | Qt.WindowType.WindowStaysOnTopHint)
        self.setWindowTitle("AIRTYPE X ? FLOATING KEYBOARD"); self.setStyleSheet("QWidget{background:#101720;color:#d8faff} QPushButton{background:#172b38;border:1px solid #00c8e8;border-radius:7px;padding:12px;color:#e8fbff} QPushButton:hover{background:#07516a}")
        root=QVBoxLayout(self); grid=QGridLayout(); root.addLayout(grid)
        for row, letters in enumerate(("1234567890", "QWERTYUIOP","ASDFGHJKL","ZXCVBNM", "!@#$%^&*()")):
            for col,key in enumerate(letters):
                b=QPushButton(key); b.clicked.connect(lambda checked=False,k=key:on_key(k)); grid.addWidget(b,row,col)
        for col,key in enumerate(("Space","Enter","Backspace","Shift","Caps Lock")):
            b=QPushButton(key); b.clicked.connect(lambda checked=False,k=key:on_key(k)); grid.addWidget(b,5,col)
        self.setMinimumWidth(650)
