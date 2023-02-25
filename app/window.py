import ctypes
import json
import os.path

import pyvscode
from PyQt5 import uic, QtGui
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QCursor
from PyQt5.QtWidgets import *
from qframelesswindow import FramelessWindow

from app import utils
from app.components.templateitem import TemplateItem
from app.components.titlebar import TitleBar
from app.components.variableinput import VariableInput
from app.src import templatoron
from app.src.templatoron import TemplatoronResponse


class TemplatoronWindow(FramelessWindow):
    # ===================================================================================
    # WIDGETS
    # ===================================================================================

    MainFrame: QFrame
    MainContentFrame: QFrame
    OutputPathButton: QPushButton
    CreateProjectBtn: QPushButton
    OutputPathInput: QLineEdit
    CheckVSCode: QCheckBox
    CheckFileExplorer: QCheckBox
    TemplateListView: QListWidget
    DirectoryDisplay: QTreeWidget
    VariableListContent: QWidget
    # WIDGETS TO SHADOW
    TemplateLabel: QLabel
    DirectoryDisplayLabel: QLabel
    VariableListLabel: QLabel

    # ===================================================================================
    # INIT
    # ===================================================================================

    def __init__(self, app: QApplication):
        super().__init__()
        self.app = app
        uic.loadUi(os.path.join(__file__, os.path.pardir, "design", "main_window.ui"), self)
        self.loadConfiguration()
        self.shadowEngine()
        for font in ["inter.ttf", "firacode.ttf"]:
            QtGui.QFontDatabase.addApplicationFont(os.path.join(__file__, os.path.pardir, "fonts", font))
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("me.KrazyManJ.Templatoron.1.0.0")
        self.setTitleBar(TitleBar(self))
        self.OutputPathButton.clicked.connect(self.change_path)
        self.CreateProjectBtn.clicked.connect(self.create_project)
        utils.center_widget(self.app, self)
        pths = "templates"
        for a in os.listdir(pths):
            self.TemplateListView.addItem(TemplateItem(os.path.abspath(os.path.join(pths, a))))
        self.TemplateListView.itemSelectionChanged.connect(self.handle_item_selection_changed)
        self.set_content_state(False)

        if not pyvscode.is_present():
            self.CheckVSCode.deleteLater()


    # ===================================================================================
    # SHADOW ENGINE
    # ===================================================================================

    def shadowEngine(self):
        utils.apply_shadow(self.TemplateLabel, 20, r=30)
        utils.apply_shadow(self.DirectoryDisplayLabel, 40)
        utils.apply_shadow(self.VariableListLabel, 40)
        utils.apply_shadow(self.CreateProjectBtn, 40)

    # ===================================================================================
    # CONFIGURATION LOADER/SAVER
    # ===================================================================================

    @staticmethod
    def defaultPath():
        if os.name == "nt":
            return os.path.join(os.path.join(os.environ['USERPROFILE']), 'Desktop')
        return os.path.expanduser("~/Desktop")

    def loadConfiguration(self):
        data: dict = json.load(open("configuration.json", "r"))
        oPath = os.path.abspath(data.get("output_path",self.defaultPath()))
        if os.path.isdir(oPath):
            self.OutputPathInput.setText(oPath)
        self.CheckFileExplorer.setChecked(data.get("open_file_explorer", False))
        self.CheckVSCode.setChecked(data.get("open_vscode", False))

    def saveConfiguration(self):
        json.dump({
            "output_path": self.OutputPathInput.text(),
            "open_file_explorer": self.CheckFileExplorer.isChecked(),
            "open_vscode": self.CheckVSCode.isChecked()
        }, open("configuration.json", "w"), indent=4)

    def closeEvent(self, a0: QtGui.QCloseEvent) -> None:
        self.saveConfiguration()

    # ===================================================================================
    # PATH CHANGER
    # ===================================================================================

    def change_path(self):
        a = QFileDialog.getExistingDirectory(self, "Select Directory", self.OutputPathInput.text())
        if a != "":
            self.OutputPathInput.setText(os.path.abspath(a))

    # ===================================================================================
    # PROJECT CREATION
    # ===================================================================================

    def create_project(self):
        if not self.is_something_selected():
            return
        if len([i for i in self.get_variables() if i.is_empty()]) == 0:
            temp = self.get_selected().Template
            pth = self.OutputPathInput.text()
            varvals = {i.get_id(): i.get_value() for i in self.get_variables()}
            respath = os.path.join(pth, templatoron.parse_variable_values(list(temp.structure.keys())[0], varvals))
            response = temp.create_project(self.OutputPathInput.text(), **varvals)
            box = QMessageBox()
            if response is TemplatoronResponse.ACCESS_DENIED:
                utils.DialogCreator.Warn("Access denied by operating system while trying to create project!")
                return
            if response is TemplatoronResponse.ALREADY_EXIST:
                utils.DialogCreator.Warn("There is already existing project with these parameters!")
                return
            utils.DialogCreator.Info("Successfully created project!")
            if self.CheckFileExplorer.isChecked():
                os.system(f'explorer /select,"{respath}"')
            if self.CheckVSCode.isChecked():
                pyvscode.open_folder(respath)
            self.close()

    # ===================================================================================
    # TREE VIEW
    # ===================================================================================

    def update_tree_view(self):
        self.DirectoryDisplay.clear()
        temp = self.get_selected().Template

        def r(parent: QTreeWidget | QTreeWidgetItem, data: dict):
            for k, v in data.items():
                varvals = {i.get_id(): i.get_value() for i in self.get_variables() if not i.is_empty()}
                currP = QTreeWidgetItem([templatoron.parse_variable_values(k, varvals)])
                if isinstance(parent, QTreeWidget):
                    parent.addTopLevelItem(currP)
                elif isinstance(parent, QTreeWidgetItem):
                    parent.addChild(currP)
                if isinstance(v, dict):
                    r(currP, v)
                elif isinstance(v, str):
                    currP.setToolTip(0, templatoron.parse_variable_values(v, varvals))

        r(self.DirectoryDisplay, temp.structure)
        self.DirectoryDisplay.expandAll()

    # ===================================================================================
    # PARAMETERS
    # ===================================================================================

    def get_variables(self) -> list[VariableInput]:
        return [i for i in self.VariableListContent.children() if isinstance(i, VariableInput)]

    def variableChange(self):
        self.update_tree_view()
        self.set_create_button_state(len([i for i in self.get_variables() if i.is_empty()]) == 0)

    # ===================================================================================
    # TEMPLATE SELECTION
    # ===================================================================================

    def is_something_selected(self):
        selected_items = self.TemplateListView.selectedItems()
        return selected_items is not None

    def get_selected(self) -> TemplateItem:
        return self.TemplateListView.selectedItems()[0]  # type: ignore

    def handle_item_selection_changed(self):
        if not self.is_something_selected():
            return
        self.set_content_state(True)
        for child in self.get_variables():
            self.VariableListContent.layout().removeWidget(child)
            child.deleteLater()
        for var in self.get_selected().Template.variables:
            mask = self.get_selected().Template.is_var_used_in_file_system(var["id"])
            self.VariableListContent.layout().addWidget(
                VariableInput(self, var["id"], var["displayname"], file_mask=mask)
            )
        self.update_tree_view()
        self.set_create_button_state(len([i for i in self.get_variables() if i.is_empty()]) == 0)

    # ===================================================================================
    # STATES CHANGES
    # ===================================================================================

    def set_content_state(self, state: bool):
        opacity_effect = QGraphicsOpacityEffect()
        opacity_effect.setOpacity(0.5)
        self.MainFrame.setGraphicsEffect(None if state else opacity_effect)
        self.MainContentFrame.setEnabled(state)
        self.MainFrame.setCursor(QCursor(Qt.ArrowCursor if state else Qt.ForbiddenCursor))

    def set_create_button_state(self, state: bool):
        opacity_effect = QGraphicsOpacityEffect()
        opacity_effect.setOpacity(0.5)
        self.CreateProjectBtn.setGraphicsEffect(None if state else opacity_effect)
        self.CreateProjectBtn.setCursor(QCursor(Qt.PointingHandCursor if state else Qt.ForbiddenCursor))
        self.CreateProjectBtn.setToolTip(None if state else "You need to enter all parameters before creation.")
