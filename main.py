from __future__ import annotations

import sys

from PySide6.QtWidgets import QApplication

from communication_database_converter.ui.main_window import MainWindow


def main() -> int:
    app = QApplication(sys.argv)
    app.setApplicationName("Communication Database Converter")
    window = MainWindow()
    window.show()
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
