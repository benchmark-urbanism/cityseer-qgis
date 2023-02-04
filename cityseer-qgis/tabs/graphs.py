""" """
from __future__ import annotations

from qgis.core import QgsVectorLayer
from qgis.PyQt import QtWidgets


class GraphsTab(QtWidgets.QWidget):
    decomp_input_netw: QgsVectorLayer | None
    decomp_dist: int | None

    def __init__(self, parent: QtWidgets.QWidget | None = None):
        """ """
        super().__init__(parent)
        layout = QtWidgets.QVBoxLayout(self)
