""" """
from __future__ import annotations

import os.path
from pathlib import Path
from typing import Any, Callable

from qgis.core import (
    Qgis,
    QgsApplication,
    QgsCoordinateReferenceSystem,
    QgsCoordinateTransform,
    QgsFeature,
    QgsFillSymbol,
    QgsGeometry,
    QgsMapLayerProxyModel,
    QgsMessageLog,
    QgsProject,
    QgsRectangle,
    QgsVectorLayer,
    QgsWkbTypes,
)
from qgis.gui import QgisInterface, QgsFileWidget, QgsMapLayerComboBox, QgsProjectionSelectionWidget
from qgis.PyQt import QtCore, QtWidgets
from qgis.PyQt.QtCore import QCoreApplication, QSettings, Qt, QTranslator, qVersion
from qgis.PyQt.QtGui import QIcon
from qgis.PyQt.QtWidgets import QAction, QToolBar, QWidget

from .dialog import CityseerDialog


class CityseerAdaptor:
    """ """

    iface: QgisInterface
    plugin_dir: str
    dlg: CityseerDialog
    actions: list[QAction]
    menu: str
    toolbar: QToolBar

    def __init__(self, iface: QgisInterface):
        """Constructor.

        :param iface: An interface instance that will be passed to this class
            which provides the hook by which you can manipulate the QGIS
            application at run time.
        :type iface: QgsInterface
        """
        # reference to the QGIS interface
        self.iface = iface
        # initialize plugin directory
        self.plugin_dir = os.path.dirname(__file__)
        # locale
        locale = QSettings().value("locale/userLocale")[0:2]
        locale_path = os.path.join(self.plugin_dir, "i18n", "Futurb_{}.qm".format(locale))
        if os.path.exists(locale_path):
            self.translator = QTranslator()
            self.translator.load(locale_path)
            if qVersion() > "4.3.3":
                QCoreApplication.installTranslator(self.translator)
        self.dlg = CityseerDialog()
        self.actions = []
        self.menu = self.tr("&Cityseer")
        self.toolbar = self.iface.addToolBar("Cityseer")
        self.toolbar.setObjectName("Cityseer")

    def tr(self, message: str):
        """Get the translation for a string using Qt translation API.

        We implement this ourselves since we do not inherit QObject.

        :param message: String for translation.
        :type message: str, QString

        :returns: Translated version of message.
        :rtype: QString
        """
        return QCoreApplication.translate("Cityseer", message)

    def add_action(
        self,
        icon_path: str,
        text: str,
        callback: Callable[[Any], Any],
        enabled_flag: bool = True,
        add_to_menu: bool = True,
        add_to_toolbar: bool = True,
        status_tip: str | None = None,
        whats_this: str | None = None,
        parent: QWidget | None = None,
    ):
        """ """
        icon = QIcon(icon_path)
        action = QAction(icon, text, parent)
        action.triggered.connect(callback)
        action.setEnabled(enabled_flag)
        if status_tip is not None:
            action.setStatusTip(status_tip)
        if whats_this is not None:
            action.setWhatsThis(whats_this)
        if add_to_toolbar:
            self.toolbar.addAction(action)
        if add_to_menu:
            self.iface.addPluginToMenu(self.menu, action)
        self.actions.append(action)

        return action

    def initGui(self):
        """ """
        icon_path = Path(os.path.dirname(__file__)) / "icon.png"
        self.add_action(str(icon_path), text=self.tr("Cityseer"), callback=self.run, parent=self.iface.mainWindow())

    def unload(self):
        """ """
        for action in self.actions:
            self.iface.removePluginMenu(self.tr("&Cityseer"), action)
            self.iface.removeToolBarIcon(action)
        del self.toolbar

    def run(self):
        """ """
        self.iface.addDockWidget(Qt.RightDockWidgetArea, self.dlg)
        # result: int = self.dlg.exec_()
        # if result:
        #     print("result")
        # else:
        #     QgsMessageLog.logMessage("No input for Cityseer dialogue to process.", level=Qgis.Warning, notifyUser=True)
