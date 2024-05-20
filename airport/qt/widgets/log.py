from __future__ import annotations

import re
import os
from typing import AnyStr
from portage.package.ebuild.config import config as portage_config
from PySide6.QtCore import Qt
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import (
    QHBoxLayout,
    QGridLayout,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QPushButton,
    QSplitter,
    QTextEdit,
    QWidget,
)

from airport.util.color import ColorType, SystemColorScheme


class LogEntry:
    ENTRY_REGEX = re.compile(r"^(LOG:|INFO:|WARN:|ERROR:)", re.MULTILINE)

    @staticmethod
    def from_str(raw: str) -> list[LogEntry]:
        entry_iters = list(LogEntry.ENTRY_REGEX.finditer(raw))
        entries = []

        for i, entry in enumerate(entry_iters):
            elog_class: int

            if entry.group() == "LOG:":
                elog_class = ColorType.COLOR_TEXT_LINK
            elif entry.group() == "INFO:":
                elog_class = ColorType.COLOR_TEXT_POSITIVE
            elif entry.group() == "WARN:":
                elog_class = ColorType.COLOR_TEXT_NEUTRAL
            else:
                elog_class = ColorType.COLOR_TEXT_NEGATIVE

            if i >= len(entry_iters) - 1:
                entries.append(LogEntry(">>>" + raw[entry.end() :], elog_class))
            else:
                entries.append(
                    LogEntry(
                        ">>>" + raw[entry.end() : entry_iters[i + 1].start()],
                        elog_class,
                    )
                )

        return entries

    def __init__(self, message: str, color: ColorType):
        self.message = message
        self.color = color

    def get_message(self) -> str:
        return self.message

    def get_color(self) -> ColorType:
        return self.color


class AirportLog(QWidget):
    def __init__(self):
        super().__init__()

        layout = QHBoxLayout()
        self.setLayout(layout)

        log_nav = QWidget()
        log_nav_layout = QGridLayout()
        log_nav.setLayout(log_nav_layout)
        splitter = QSplitter(Qt.Orientation.Horizontal)

        log_search = QLineEdit()
        log_search.setPlaceholderText("Search for content...")
        log_filter = QPushButton(QIcon.fromTheme("dialog-filters"), "Filter")
        log_entries = QListWidget()

        log_files = sorted(
            self._generate_log_list(), key=lambda x: os.path.getmtime(x), reverse=True
        )
        for log_path in log_files:
            list_item = QListWidgetItem(os.path.basename(log_path))
            list_item.setData(1, log_path)
            log_entries.addItem(list_item)

        log_search.textChanged.connect(self.search_log_files)
        log_entries.currentItemChanged.connect(self.update_log_contents)

        log_nav_layout.addWidget(log_search, 0, 0)
        log_nav_layout.addWidget(log_filter, 0, 1)
        log_nav_layout.addWidget(log_entries, 1, 0, 1, 2)

        log_view_container = QWidget()
        log_view_layout = QHBoxLayout()
        log_view = QTextEdit()
        log_view.setReadOnly(True)
        log_view.setFontFamily("monospace")
        log_view.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
        log_view_layout.addWidget(log_view)
        log_view_container.setLayout(log_view_layout)

        splitter.addWidget(log_nav)
        splitter.addWidget(log_view_container)
        splitter.setCollapsible(0, False)
        splitter.setCollapsible(1, False)
        splitter.setStretchFactor(0, 0)
        splitter.setStretchFactor(1, 1)
        splitter.moveSplitter(400, 1)
        layout.addWidget(splitter)

        self.log_files = log_files
        self.log_entries = log_entries
        self.log_view = log_view
        self.colors = SystemColorScheme()

    def search_log_files(self, text: str):
        self.log_entries.clear()

        for entry in self.log_files:
            filename = os.path.basename(entry)
            if text in filename:
                item = QListWidgetItem(filename)
                item.setData(1, entry)
                self.log_entries.addItem(item)

    def update_log_contents(self, item: QListWidgetItem):
        if item is None:
            return

        self.log_view.clear()
        with open(item.data(1), "r") as f:
            entries = LogEntry.from_str(f.read())

            for entry in entries:
                self.log_view.setTextColor(self.colors.get_color(entry.get_color()))
                self.log_view.append(entry.get_message() + "\n")

    def _generate_log_list(self) -> list[AnyStr]:
        conf = portage_config()
        return self._collect_log_files(
            os.path.abspath(
                os.path.join(conf.get("PORTAGE_LOGDIR", "/var/log/portage"), "elog")
            )
        )

    def _collect_log_files(self, path: AnyStr) -> list[AnyStr]:
        collected_files = []

        for entry in os.scandir(path):
            if entry.is_dir():
                collected_files.extend(
                    self._collect_log_files(os.path.join(path, entry.name))
                )
            elif entry.name.endswith(".log"):
                collected_files.append(os.path.abspath(os.path.join(path, entry.name)))

        return collected_files
