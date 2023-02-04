""" """
from __future__ import annotations

from qgis.gui import QgisInterface

from .adaptor import CityseerAdaptor


def classFactory(iface: QgisInterface):
    """ """
    return CityseerAdaptor(iface)
