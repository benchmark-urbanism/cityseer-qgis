""" """
from __future__ import annotations

import os
from pathlib import Path

os.environ["CITYSEER_QUIET_MODE"] = "1"

from cityseer.tools import io
from qgis.core import (
    Qgis,
    QgsCoordinateReferenceSystem,
    QgsFeature,
    QgsMapLayerProxyModel,
    QgsMessageLog,
    QgsVectorLayer,
    QgsWkbTypes,
)
from qgis.gui import QgsMapLayerComboBox
from qgis.PyQt import QtWidgets
from shapely import geometry, wkt


class ByRadiusTab(QtWidgets.QWidget):
    """ """

    easting: int | None
    northing: int | None
    radius: int | None
    poly: geometry.Polygon | None
    easting_input: QtWidgets.QLineEdit
    northing_input: QtWidgets.QLineEdit
    radius_input: QtWidgets.QLineEdit
    extents_feedback: QtWidgets.QLabel

    def __init__(self, parent: QtWidgets.QWidget | None = None):
        """ """
        super().__init__(parent)
        self.easting = None
        self.northing = None
        self.radius = None
        self.poly = None
        layout = QtWidgets.QVBoxLayout(self)
        layout.addWidget(QtWidgets.QLabel("Easting"))
        self.easting_input = QtWidgets.QLineEdit("")
        self.easting_input.textChanged.connect(self.handle_extents)
        layout.addWidget(self.easting_input)
        layout.addWidget(QtWidgets.QLabel("Northing"))
        self.northing_input = QtWidgets.QLineEdit("")
        self.northing_input.textChanged.connect(self.handle_extents)
        layout.addWidget(self.northing_input)
        layout.addWidget(QtWidgets.QLabel("Radius"))
        self.radius_input = QtWidgets.QLineEdit("")
        self.radius_input.textChanged.connect(self.handle_extents)
        layout.addWidget(self.radius_input)
        self.extents_feedback = QtWidgets.QLabel("Specify location and radius")
        layout.addWidget(self.extents_feedback)
        layout.addStretch(1)

    def handle_extents(self) -> None:
        """ """
        try:
            self.easting = int(self.easting_input.text())
            self.northing = int(self.northing_input.text())
            self.radius = int(self.radius_input.text())
            self.poly = geometry.Point(self.easting, self.northing).buffer(self.radius)
        except Exception:
            self.easting = None
            self.northing = None
            self.radius = None
            self.poly = None
            QgsMessageLog.logMessage(
                f"Unable to parse easting: {self.easting_input.text()}, "
                f"northing: {self.northing_input.text()}, "
                f"radius: {self.radius_input.text()} to ints",
                level=Qgis.Warning,
                notifyUser=True,
            )


class ByPolyTab(QtWidgets.QWidget):
    """ """

    poly: geometry.Polygon | None
    poly_input_extents: QgsMapLayerComboBox
    poly_input_feedback: QtWidgets.QLabel

    def __init__(self, parent: QtWidgets.QWidget | None = None):
        """ """
        super().__init__(parent)
        self.poly = None
        layout = QtWidgets.QVBoxLayout(self)
        layout.addWidget(QtWidgets.QLabel("Extents polygon"))
        self.poly_input_extents = QgsMapLayerComboBox(self)
        self.poly_input_extents.setFilters(QgsMapLayerProxyModel.PolygonLayer)
        self.poly_input_extents.setShowCrs(True)
        self.poly_input_extents.layerChanged.connect(self.handle_poly_extents)
        layout.addWidget(self.poly_input_extents)
        self.poly_input_feedback = QtWidgets.QLabel("Select an extents Polygon")
        layout.addWidget(self.poly_input_feedback)
        layout.addStretch(1)

    def handle_poly_extents(self) -> None:
        """ """
        self.poly = None
        # check geometry
        candidate_layer: QgsVectorLayer = self.poly_input_extents.currentLayer()
        geom_type: QgsWkbTypes.GeometryType = candidate_layer.geometryType()  # type: ignore
        if not isinstance(candidate_layer, QgsVectorLayer) or geom_type != QgsWkbTypes.PolygonGeometry:
            self.poly_input_feedback.setText("Polygon Layer required.")
            return
        # success
        self.poly_input_feedback.setText("")
        feature: QgsFeature
        for feature in candidate_layer.getFeatures():
            geom_wkt = feature.geometry().asWkt()
            self.poly = wkt.loads(geom_wkt)
            break


class OsmTab(QtWidgets.QWidget):
    """ """

    buffer_dist: int | None
    filename: str | None
    parent_working_dir_path: Path | None
    parent_crs_selection: QgsCoordinateReferenceSystem | None
    tabs: QtWidgets.QTabWidget
    radius_tab: ByRadiusTab
    poly_tab: ByPolyTab
    buffer_dist_input: QtWidgets.QLineEdit
    filename_input: QtWidgets.QLineEdit
    import_btn: QtWidgets.QPushButton
    extents_poly: geometry.Polygon | geometry.MultiPolygon | None

    def __init__(self, parent: QtWidgets.QWidget):
        """ """
        super().__init__(parent)
        self.buffer_dist = None
        self.filename = None
        self.parent_working_dir_path = None
        self.parent_crs_selection = None
        # inputs
        layout = QtWidgets.QVBoxLayout(self)
        layout.addWidget(QtWidgets.QLabel("Extents selection method"))
        self.tabs = QtWidgets.QTabWidget()
        self.radius_tab = ByRadiusTab()
        self.tabs.addTab(self.radius_tab, "By Radius")
        self.poly_tab = ByPolyTab()
        self.tabs.addTab(self.poly_tab, "By Poly")
        layout.addWidget(self.tabs)
        self.tabs.currentChanged.connect(self.handle_params)
        layout.addWidget(QtWidgets.QLabel("Buffer distance"))
        self.buffer_dist_input = QtWidgets.QLineEdit("")
        self.buffer_dist_input.textChanged.connect(self.handle_params)
        layout.addWidget(self.buffer_dist_input)
        layout.addWidget(QtWidgets.QLabel("Output filename"))
        self.filename_input = QtWidgets.QLineEdit("")
        self.filename_input.textChanged.connect(self.handle_params)
        layout.addWidget(self.filename_input)
        # action button
        self.import_btn = QtWidgets.QPushButton("Import")
        self.import_btn.setDisabled(True)
        self.import_btn.pressed.connect(self.process_import)
        layout.addWidget(self.import_btn)
        layout.addStretch(1)

    def update_child(self, working_dir_path: Path | None, crs_selection: QgsCoordinateReferenceSystem | None) -> None:
        """ """
        self.parent_working_dir_path = working_dir_path
        self.parent_crs_selection = crs_selection
        self.handle_params()

    def handle_params(self) -> None:
        """ """
        self.import_btn.setDisabled(True)
        # check if buffer distance and file name have been provided
        try:
            self.buffer_dist = int(self.buffer_dist_input.text())
            self.filename = self.filename_input.text()
        except Exception:
            return
        if self.filename == "":
            return
        # check that extents are available via tabs
        current_tab = self.tabs.currentWidget()
        if isinstance(current_tab, ByRadiusTab):
            self.extents_poly = self.radius_tab.poly
        else:
            self.extents_poly = self.poly_tab.poly
        if self.extents_poly is None:
            return
        # check that working directory and CRS are available via parent
        if self.parent_working_dir_path is None:
            return
        if self.parent_crs_selection is None:
            return
        self.import_btn.setDisabled(False)

    def process_import(self) -> None:
        """ """
        QgsMessageLog.logMessage("Fetching OSM data for specified extents.", level=Qgis.Warning, notifyUser=True)
        epsg_code = int(self.parent_crs_selection.authid().split(":")[-1])
        osm_nx = io.osm_graph_from_poly(
            self.extents_poly, poly_epsg_code=epsg_code, to_epsg_code=epsg_code, simplify=True
        )
        print(osm_nx)
