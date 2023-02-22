import ctypes
import os.path

from PyQt5 import uic, QtGui
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QCursor
from PyQt5.QtWidgets import *
from qframelesswindow import FramelessWindow

from app.src import templatoron
from app import utils
from app.components.templateitem import TemplateItem
from app.components.titlebar import TitleBar
from app.components.variableinput import VariableInput


class TemplatoronWindow(FramelessWindow):
    MainFrame: QFrame
    MainContentFrame: QFrame

    OutputPathButton: QPushButton
    CreateProjectBtn: QPushButton
    OutputPathInput: QLineEdit

    TemplateListView: QListWidget

    DirectoryDisplay: QTreeWidget

    VariableListContent: QWidget

    def __init__(self, app):
        super().__init__()
        self.app = app
        uic.loadUi(os.path.join(__file__, os.path.pardir, "design", "main_window.ui"), self)
        for font in ["inter.ttf", "firacode.ttf"]:
            QtGui.QFontDatabase.addApplicationFont(os.path.join(__file__, os.path.pardir, "fonts", font))
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("me.KrazyManJ.Templatoron.1.0.0")
        self.setTitleBar(TitleBar(self))
        self.OutputPathButton.clicked.connect(self.change_path)
        self.CreateProjectBtn.clicked.connect(self.create_project)
        utils.center_widget(self.app, self)
        self.OutputPathInput.setText(os.path.join(os.path.join(os.environ['USERPROFILE']), 'Desktop'))
        pths = "templates"
        for a in os.listdir(pths):
            self.TemplateListView.addItem(TemplateItem(os.path.abspath(os.path.join(pths, a))))
        self.TemplateListView.itemSelectionChanged.connect(self.handle_item_selection_changed)
        self.set_content_state(False)

    def change_path(self):
        a = QFileDialog.getExistingDirectory(self, "Select Directory", self.OutputPathInput.text())
        if a != "":
            self.OutputPathInput.setText(os.path.abspath(a))

    def create_project(self):
        if not self.is_something_selected():
            return
        if len([i for i in self.get_variables() if i.is_empty()]) == 0:
            temp = self.get_selected().Template
            pth = self.OutputPathInput.text()
            varvals = {i.get_id(): i.get_value() for i in self.get_variables()}
            respath = os.path.join(pth, templatoron.parse_variable_values(list(temp.structure.keys())[0], varvals))
            temp.create_project(self.OutputPathInput.text(), **varvals)
            os.system(f'explorer /select,"{respath}"')
            self.close()

    def update_tree_view(self):
        self.DirectoryDisplay.clear()
        temp = self.get_selected().Template

        def r(parent: QTreeWidget | QTreeWidgetItem, data: dict):
            for k, v in data.items():
                currP = QTreeWidgetItem([
                    templatoron.parse_variable_values(k, {i.get_id(): i.get_value() for i in self.get_variables() if not i.is_empty()})
                ])
                if isinstance(parent, QTreeWidget):
                    parent.addTopLevelItem(currP)
                elif isinstance(parent, QTreeWidgetItem):
                    parent.addChild(currP)
                if isinstance(v, dict):
                    r(currP, v)


        r(self.DirectoryDisplay, temp.structure)
        self.DirectoryDisplay.expandAll()

    def get_variables(self) -> list[VariableInput]:
        return [i for i in self.VariableListContent.children() if isinstance(i, VariableInput)]

    def variableChange(self):
        self.update_tree_view()
        self.set_create_button_state(len([i for i in self.get_variables() if i.is_empty()]) == 0)

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
            self.VariableListContent.layout().addWidget(VariableInput(self, var["id"], var["displayname"]))
        self.update_tree_view()
        self.set_create_button_state(len([i for i in self.get_variables() if i.is_empty()]) == 0)

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