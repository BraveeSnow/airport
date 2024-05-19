#!/usr/bin/env python

import sys
from portage.package.ebuild.config import config as PortageConfig
from signal import signal, SIGINT, SIG_DFL
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import (
    QApplication,
    QVBoxLayout,
    QMainWindow,
    QTabWidget,
    QWidget,
)

from widgets.use import AirportUse
from widgets.log import AirportLog


class AirportMainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Airport")

        main_layout = QVBoxLayout()
        main_widget = QWidget()
        main_widget.setLayout(main_layout)

        tabs = QTabWidget()
        main_layout.addWidget(tabs)

        use_flag_tab = AirportUse()
        use_flag_icon = QIcon.fromTheme("flag")
        tabs.addTab(use_flag_tab, use_flag_icon, "USE Flags")

        log_tab = AirportLog()
        log_icon = QIcon.fromTheme("documentation")
        tabs.addTab(log_tab, log_icon, "Logs")

        self.setCentralWidget(main_widget)


if __name__ == "__main__":
    signal(SIGINT, SIG_DFL)

    app = QApplication(sys.argv)
    main_window = AirportMainWindow()
    main_window.resize(1000, 600)
    main_window.show()
    sys.exit(app.exec())
