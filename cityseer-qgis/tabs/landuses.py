""" """
from __future__ import annotations

from qgis.core import QgsVectorLayer
from qgis.PyQt import QtWidgets


class LandusesTab(QtWidgets.QWidget):
    lus_cent_input_netw: QgsVectorLayer | None
    lus_input_layer: QgsVectorLayer | None
    lus_distances: list[int]

    def __init__(self, parent: QtWidgets.QWidget | None = None):
        """ """
        super().__init__(parent)
        layout = QtWidgets.QVBoxLayout(self)
