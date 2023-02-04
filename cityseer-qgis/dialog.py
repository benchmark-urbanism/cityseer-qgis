""" """
from __future__ import annotations

from pathlib import Path

from qgis.core import QgsCoordinateReferenceSystem
from qgis.gui import QgsFileWidget, QgsProjectionSelectionWidget
from qgis.PyQt import QtCore, QtWidgets

from .tabs.centrality import CentralityTab
from .tabs.graphs import GraphsTab
from .tabs.landuses import LandusesTab
from .tabs.osm import OsmTab


class CityseerDialog(QtWidgets.QDockWidget):
    """ """

    working_dir: QgsFileWidget
    working_dir_feedback: QtWidgets.QLabel
    crs_dropdown: QgsProjectionSelectionWidget
    crs_feedback: QtWidgets.QLabel
    osm_tab: OsmTab
    graphs_tab: GraphsTab
    cent_tab: CentralityTab
    lus_tab: LandusesTab
    working_dir_path: Path | None
    crs_selection: QgsCoordinateReferenceSystem | None

    def __init__(self, parent: QtWidgets.QWidget | None = None) -> None:
        """ """
        super().__init__(parent)
        self.working_dir_path = None
        self.crs_selection = None
        # layout
        self.setWindowTitle("Cityseer QGIS Plugin")
        self.setAllowedAreas(QtCore.Qt.RightDockWidgetArea)
        # DockWidget doesn't have set layout - use Widget and setWidget
        dw_content = QtWidgets.QWidget()
        # main layout for dock widget
        dw_layout = QtWidgets.QVBoxLayout(dw_content)
        # working directory sub-content / layout
        work_dir_content = QtWidgets.QGroupBox("Project working directory")
        work_dir_layout = QtWidgets.QVBoxLayout(work_dir_content)
        self.working_dir = QgsFileWidget(self)
        self.working_dir.setStorageMode(QgsFileWidget.GetDirectory)
        self.working_dir.fileChanged.connect(self.handle_working_dir)
        work_dir_layout.addWidget(self.working_dir)
        self.working_dir_feedback = QtWidgets.QLabel("Specify working directory", self)
        self.working_dir_feedback.setWordWrap(True)
        work_dir_layout.addWidget(self.working_dir_feedback)
        # add to dock widget layout
        dw_layout.addWidget(work_dir_content)
        # CRS
        crs_content = QtWidgets.QGroupBox("Project Coordinate Reference System")
        crs_layout = QtWidgets.QVBoxLayout(crs_content)
        crs_layout.addWidget(QtWidgets.QLabel("CRS to use for analysis"))
        self.crs_dropdown = QgsProjectionSelectionWidget(self)
        self.crs_dropdown.crsChanged.connect(self.handle_crs)
        self.crs_dropdown.setOptionVisible(QgsProjectionSelectionWidget.CurrentCrs, False)
        self.crs_dropdown.setOptionVisible(QgsProjectionSelectionWidget.DefaultCrs, False)
        self.crs_dropdown.setOptionVisible(QgsProjectionSelectionWidget.LayerCrs, True)
        self.crs_dropdown.setOptionVisible(QgsProjectionSelectionWidget.ProjectCrs, True)
        self.crs_dropdown.setOptionVisible(QgsProjectionSelectionWidget.RecentCrs, False)
        crs_layout.addWidget(self.crs_dropdown)
        self.crs_feedback = QtWidgets.QLabel("Specify CRS")
        self.crs_feedback.setWordWrap(True)
        crs_layout.addWidget(self.crs_feedback)
        # trigger first run
        self.handle_crs()
        # add to dock widget layout
        dw_layout.addWidget(crs_content)
        # prepare tabs
        tabs = QtWidgets.QTabWidget()
        self.osm_tab = OsmTab(self)
        tabs.addTab(self.osm_tab, "OSM import")
        self.graphs_tab = GraphsTab(self)
        tabs.addTab(self.graphs_tab, "Graphs")
        self.cent_tab = CentralityTab(self)
        tabs.addTab(self.cent_tab, "Centrality")
        self.lus_tab = LandusesTab(self)
        tabs.addTab(self.lus_tab, "Land Uses")
        # add to dock widget layout
        dw_layout.addWidget(tabs)
        # add dock content widget to self (DockWidget)
        self.setWidget(dw_content)

    def handle_working_dir(self) -> None:
        """ """
        self.update_child_tabs()
        out_path: Path = Path(self.working_dir.filePath().strip())
        if not out_path.exists() or not out_path.is_dir():
            self.working_dir_feedback.setText("Filepath directory does not exist.")
            self.working_dir_path = None
        else:
            self.working_dir_feedback.setText("")
            self.working_dir_path = out_path.parent.absolute()
        self.update_child_tabs()

    def handle_crs(self) -> None:
        """ """
        # error if not instantiated yet?
        if not hasattr(self, "crs_feedback"):
            return
        if self.crs_dropdown.crs().isGeographic():
            self.crs_feedback.setText("Requires a projected (not geographic) CRS")
            self.crs_selection = None
        else:
            self.crs_feedback.setText("")
            self.crs_selection = self.crs_dropdown.crs()
        self.update_child_tabs()

    def update_child_tabs(self) -> None:
        """ """
        if not hasattr(self, "osm_tab"):
            return
        self.osm_tab.update_child(self.working_dir_path, self.crs_selection)
