from dataclasses import dataclass
from portage.dbapi.porttree import portdbapi as PortageTree
from portage.versions import cpv_getversion
from PySide6.QtCore import Qt
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import (
    QHBoxLayout,
    QGridLayout,
    QLineEdit,
    QPushButton,
    QSplitter,
    QTreeWidget,
    QTreeWidgetItem,
    QWidget,
)


@dataclass
class Package:
    """Data class for package information obtained from portage's dbapi."""

    name: str
    category: str
    versions: list[str]
    repos: list[str]


class AirportUse(QWidget):
    def __init__(self):
        super().__init__()
        self.porttree = PortageTree()

        # May cause long start-up issues; probably a good idea to offload to
        # another thread.
        self.portage_packages = compile_package_list(self.porttree)

        main_layout = QHBoxLayout()
        self.setLayout(main_layout)

        splitter = QSplitter(Qt.Orientation.Vertical)
        main_layout.addWidget(splitter)
        upper_container = QWidget()
        upper_container_layout = QGridLayout()
        upper_container.setLayout(upper_container_layout)
        lower_container = QWidget()
        lower_container_layout = QHBoxLayout()
        lower_container.setLayout(lower_container_layout)
        splitter.addWidget(upper_container)
        splitter.addWidget(lower_container)

        # upper container children
        package_search = QLineEdit()
        package_search_trigger = QPushButton()
        package_filter = QPushButton()
        package_list = QTreeWidget()

        package_search.setPlaceholderText("Search for packages...")
        package_search.returnPressed.connect(self.search_atom)
        package_search_trigger.setText("Search")
        package_search_trigger.setIcon(QIcon.fromTheme("search"))
        package_search_trigger.clicked.connect(self.search_atom)
        package_filter.setText("Filter")
        package_filter.setIcon(QIcon.fromTheme("dialog-filters"))
        package_list.setHeaderLabels(["Name", "Repository"])

        upper_container_layout.addWidget(package_search, 0, 0)
        upper_container_layout.addWidget(package_search_trigger, 0, 1)
        upper_container_layout.addWidget(package_filter, 0, 2)
        upper_container_layout.addWidget(package_list, 1, 0, 1, 3)

        self.package_search = package_search
        self.package_list = package_list

        # lower container children
        package_meta = QTreeWidget()
        package_flags = QTreeWidget()

        package_meta.setHeaderLabels(["Meta", "Value"])
        package_flags.setHeaderLabels(["Flag", "Global", "Local"])

        lower_container_layout.addWidget(package_meta)
        lower_container_layout.addWidget(package_flags)

        self.package_meta = package_meta
        self.package_flags = package_flags

    def search_atom(self):
        self.package_list.clear()
        self.package_meta.clear()
        self.package_flags.clear()

        for package in self.portage_packages:
            if self.package_search.text() in package.name:
                self.package_list.addTopLevelItem(
                    QTreeWidgetItem(
                        [
                            "/".join([package.category, package.name]),
                            ", ".join(package.repos),
                        ]
                    )
                )


def compile_package_list(porttree: PortageTree) -> list[Package]:
    porttree.freeze()
    package_atoms = porttree.cp_all()
    packages = []

    for atom in package_atoms:
        catsplit = atom.split("/")
        repos = porttree.getRepositories(atom)
        versions = list(map(lambda p: cpv_getversion(p), porttree.cp_list(atom)))
        packages.append(Package(catsplit[1], catsplit[0], versions, repos))

    porttree.melt()
    return packages
