import sys
from PySide6.QtWidgets import QApplication
from src.ui.dashboard import Dashboard

def main():
    app=QApplication(sys.argv); app.setApplicationName("AIRTYPE X"); window=Dashboard(); window.show(); return app.exec()

if __name__ == "__main__": raise SystemExit(main())
