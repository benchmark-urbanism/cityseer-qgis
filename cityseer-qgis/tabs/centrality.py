""" """
from __future__ import annotations

from qgis.core import QgsVectorLayer
from qgis.PyQt import QtWidgets


class CentralityTab(QtWidgets.QWidget):
    cent_input_netw: QgsVectorLayer | None
    cent_methods: list[str] | None
    cent_distances: list[int] | None
    cent_angular: bool

    def __init__(self, parent: QtWidgets.QWidget | None = None):
        """ """
        super().__init__(parent)
        layout = QtWidgets.QVBoxLayout(self)
