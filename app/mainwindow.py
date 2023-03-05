import json
import os.path

import pyvscode  # type: ignore
from PyQt5 import uic, QtGui
from PyQt5.QtCore import Qt, QItemSelection, QEvent
from PyQt5.QtGui import QCursor, QIcon, QFont, QPalette, QBrush, QPixmap
from PyQt5.QtWidgets import *
from qframelesswindow import FramelessWindow
from showinfm import show_in_file_manager

from app.components.templateitem import TemplateItem
from app.components.titlebar import TitleBar
from app.components.variableinput import VariableInput
from app.components.windows.console import ConsoleWindow
from app.components.windows.createtemplate import CreateTemplate
from app.components.windows.defaultvar import DefaultVariableWindow
from app.editwindow import TemplatoronEditWindow
from app.src import templatoron, git, utils, dialog, systemsupport
from app.src.jetbrains_ides import IDEs, open_file_in_ide, is_ide_installed
from app.src.templatoron import TemplatoronResponse


class TemplatoronMainWindow(FramelessWindow):
    TEMPLATES_FOLDER = "templates"

    # ===================================================================================
    # WIDGETS
    # ===================================================================================

    MainFrame: QFrame
    MainContentFrame: QFrame
    TemplateListFrame: QFrame
    OutputPathButton: QPushButton
    CreateProjectBtn: QPushButton
    OutputPathInput: QLineEdit
    CheckCloseApp: QCheckBox
    ComboOpenVia: QComboBox
    CheckInitGit: QCheckBox
    NoTemplatesFoundLabel: QLabel
    TemplateListContent: QFrame
    TemplateListView: QTreeWidget
    DirectoryDisplay: QTreeWidget
    VariableListContent: QWidget
    TemplateLabel: QLabel
    DirectoryDisplayLabel: QLabel
    VariableListHeader: QFrame
    VariableListLabel: QLabel
    DefaultValuesBtn: QPushButton
    CreateTemplateBtn: QPushButton
    EditTemplateBtn: QPushButton

    COMBO_DATA = [("Nothing", "nothing", lambda: True), ("File Explorer", "file_explorer", lambda: True),
                  ("Visual Studio Code", "vscode", lambda: pyvscode.is_present()),
                  ("PyCharm", "pycharm", lambda: is_ide_installed(IDEs.PYCHARM)),
                  ("PhpStorm", "phpstorm", lambda: is_ide_installed(IDEs.PHPSTORM)),
                  ("IntelliJ IDEA", "idea", lambda: is_ide_installed(IDEs.INTELLIJ))]


    # ===================================================================================
    # INIT
    # ===================================================================================

    def __init__(self, app: QApplication):
        super().__init__()
        self.defaultVarValues = {}
        self.app = app
        os.makedirs(self.TEMPLATES_FOLDER, exist_ok=True)
        uic.loadUi(os.path.join(__file__, os.path.pardir, "design", "main_window.ui"), self)
        self.setTitleBar(TitleBar(self))
        self.shadowEngine()
        utils.center_widget(self.app, self)
        for name, icon, pred in self.COMBO_DATA:
            if pred():
                self.ComboOpenVia.addItem(QIcon(f":/open_via/open_icons/{icon}.svg"), name)
        self.loadConfiguration()
        self.connector()
        for font in ["inter.ttf", "firacode.ttf"]:
            QtGui.QFontDatabase.addApplicationFont(os.path.join(__file__, os.path.pardir, "fonts", font))
        self.scan_files()
        (self.TemplateListView.hide if len(
            os.listdir(self.TEMPLATES_FOLDER)) == 0 else self.NoTemplatesFoundLabel.hide)()
        self.set_content_state(False)
        self.set_create_project_button_state(False)
        self.set_edit_template_button_state(False)
        self.VariableListHeader.hide()
        self.CheckCloseApp.setIcon(QIcon(":/titlebar/titlebar/close.svg"))
        self.CheckInitGit.setIcon(QIcon(":/content/github.svg"))

        if not git.is_installed(): self.CheckInitGit.hide()

        self.TemplateListView.setContextMenuPolicy(Qt.CustomContextMenu)
        self.TemplateLabel.setFocus()
        self.installEventFilter(self)

    def eventFilter(self, obj, event):
        if event.type() == QEvent.MouseButtonPress:
            self.clearFocus()
        return super().eventFilter(obj, event)

    def connector(self):
        self.CreateTemplateBtn.clicked.connect(self.create_template)  # type: ignore
        self.OutputPathButton.clicked.connect(self.change_path)  # type: ignore
        self.CreateProjectBtn.clicked.connect(self.create_project)  # type: ignore
        self.TemplateListView.selectionChanged = self.handle_item_selection_changed  # type: ignore
        self.ComboOpenVia.currentTextChanged.connect(self.settingPropertyChanged)  # type: ignore
        self.CheckCloseApp.stateChanged.connect(self.settingPropertyChanged)  # type: ignore
        self.CheckInitGit.stateChanged.connect(self.settingPropertyChanged)  # type: ignore
        self.DefaultValuesBtn.clicked.connect(self.setDefaultParameters) # type: ignore
        self.TemplateListView.customContextMenuRequested.connect(self.templateTreeContextMenu) # type: ignore
        self.TemplateListView.mouseMoveEvent = lambda ev: None
        self.EditTemplateBtn.clicked.connect(self.edit_template) # type: ignore

    def shadowEngine(self):
        utils.apply_shadow(self.TemplateLabel, 150, r=30)
        utils.apply_shadow(self.DirectoryDisplayLabel, 40)
        utils.apply_shadow(self.VariableListLabel, 40)
        utils.apply_shadow(self.CreateProjectBtn, 40)

    # ===================================================================================
    # CONFIGURATION LOADER/SAVER
    # ===================================================================================

    def loadConfiguration(self):
        if not os.path.exists("configuration.json"):
            open("configuration.json", "w").write("{}")
        data: dict = json.load(open("configuration.json", "r"))
        oPath = os.path.abspath(data.get("output_path", systemsupport.desktop_path()))
        if os.path.isdir(oPath):
            self.OutputPathInput.setText(oPath)
        self.CheckCloseApp.setChecked(data.get("close_app", False))
        self.CheckInitGit.setChecked(data.get("init_git", False))
        open_via = data.get("open_via", "Nothing")
        available = [name for name, icon, pred in self.COMBO_DATA if pred]
        self.ComboOpenVia.setCurrentText(open_via if open_via in available else "Nothing")
        self.defaultVarValues = data.get("default_var_values", {})

    def saveConfiguration(self):
        json.dump({"output_path": self.OutputPathInput.text(), "close_app": self.CheckCloseApp.isChecked(),
                   "init_git": self.CheckInitGit.isChecked(), "open_via": self.ComboOpenVia.currentText(),
                   "default_var_values": self.defaultVarValues}, open("configuration.json", "w"), indent=4,
                  sort_keys=True)

    def closeEvent(self, a0: QtGui.QCloseEvent) -> None:
        self.saveConfiguration()

    def settingPropertyChanged(self):
        self.saveConfiguration()

    # ===================================================================================
    # PATH CHANGER
    # ===================================================================================

    def change_path(self):
        a = QFileDialog.getExistingDirectory(self, "Select Directory", self.OutputPathInput.text())  # type: ignore
        if a != "":
            self.OutputPathInput.setText(os.path.abspath(a))

    # ===================================================================================
    # PROJECT CREATION
    # ===================================================================================

    def create_project(self):
        if not self.is_template_selected():
            return
        if len([i for i in self.get_variables() if i.is_empty()]) > 0:
            return
        temp = self.get_selected().Template
        pth = self.OutputPathInput.text()
        if len(temp.commands) > 0:
            if not dialog.Confirm(
                    "This template contains terminal commands to execute after project creation and it can take some time to execute them. Do you want to continue?"):
                return
        varvals = {i.get_id(): i.get_value() for i in self.get_variables()}
        respath = os.path.join(pth, templatoron.parse_variable_values(list(temp.structure.keys())[0], varvals))
        resallpaths = [os.path.join(pth, templatoron.parse_variable_values(a, varvals)) for a in temp.structure.keys()]
        self.set_app_state(False)
        response = temp.create_project(self.OutputPathInput.text(), **varvals)
        for restype, message in [
            (TemplatoronResponse.ACCESS_DENIED, "Access denied by operating system while trying to create project!",),
            (TemplatoronResponse.ALREADY_EXIST, "There is already existing project with these parameters!",)]:
            if response == restype:
                dialog.Warn(message)
                self.set_app_state(True)
                return
        if len(temp.commands) > 0:
            ConsoleWindow(temp.commands, temp.command_path(self.OutputPathInput.text(), **varvals)).exec()
        self.set_app_state(True)
        for label, fct in {"File Explorer": lambda: show_in_file_manager(resallpaths, False),
                           "Visual Studio Code": lambda: pyvscode.open_folder(
                               *([pth, resallpaths] if len(resallpaths) > 1 else [respath])),
                           "PyCharm": lambda: open_file_in_ide(IDEs.PYCHARM, resallpaths),
                           "IntelliJ IDEA": lambda: open_file_in_ide(IDEs.INTELLIJ, resallpaths),
                           "PhpStorm": lambda: open_file_in_ide(IDEs.PHPSTORM, resallpaths)}.items():
            if self.ComboOpenVia.currentText() == label:
                fct()
                break

        if self.CheckInitGit.isChecked():
            gitpth = pth if len(resallpaths) > 1 or os.path.isfile(respath) else respath
            if not git.already_init(gitpth):
                git.init(gitpth)
            else:
                dialog.Warn("Git repository in this folder is already initialized, skipped initializing!")

        if self.CheckCloseApp.isChecked():
            self.saveConfiguration()
            self.close()

    # ===================================================================================
    # TREE VIEW
    # ===================================================================================

    def update_tree_view(self):
        self.DirectoryDisplay.clear()

        if not self.is_template_selected():
            return
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
        self.set_create_project_button_state(len([i for i in self.get_variables() if i.is_empty()]) == 0)

    def setDefaultParameters(self):
        if not self.is_template_selected():
            return
        if len(self.get_variables()) == 0:
            return
        self.set_app_state(False)
        sel = self.get_selected()
        response = DefaultVariableWindow(sel.Template, self.defaultVarValues.get(os.path.relpath(sel.path), {})).exec()
        if response is not None:
            self.defaultVarValues[os.path.relpath(sel.path)] = response
            self.saveConfiguration()
            self.unselect_template()
            self.TemplateListView.setCurrentItem(sel)
        self.set_app_state(True)

    # ===================================================================================
    # TEMPLATE SELECTION
    # ===================================================================================

    def is_template_selected(self):
        return len([a for a in self.TemplateListView.selectedItems() if isinstance(a,TemplateItem)]) == 1

    def get_selected(self) -> TemplateItem:
        return self.TemplateListView.currentItem()  # type: ignore

    def handle_item_selection_changed(self, selected: QItemSelection, deselected: QItemSelection):
        if not self.is_template_selected():
            self.unselect_template(keep_selection=True)
            return
        selected = self.TemplateListView.itemFromIndex(selected.indexes()[0]) if len(selected.indexes()) > 0 else None
        deselected = self.TemplateListView.itemFromIndex(deselected.indexes()[0]) if len(
            deselected.indexes()) > 0 else None

        if not isinstance(selected, TemplateItem):
            self.unselect_template(keep_selection=True)
            return
        self.set_content_state(True)
        self.set_edit_template_button_state(True)
        for child in self.get_variables():
            self.VariableListContent.layout().removeWidget(child)
            child.deleteLater()
        for var in selected.Template.variables:
            mask = selected.Template.is_var_used_in_file_system(var["id"])
            varInput = VariableInput(var["id"], var["displayname"], file_mask=mask)
            varInput.input.textEdited.connect(self.variableChange)
            varInput.input.setText(self.defaultVarValues.get(os.path.relpath(selected.path), {}).get(var["id"], ""))
            self.VariableListContent.layout().addWidget(varInput)
        if self.VariableListContent.layout().count() == 0:
            self.VariableListHeader.hide()
            self.set_create_project_button_state(True)
        else:
            self.VariableListHeader.show()
            self.set_create_project_button_state(len([i for i in self.get_variables() if i.is_empty()]) == 0)
        self.update_tree_view()

    def unselect_template(self, a0=None, keep_selection=False):
        for child in self.get_variables():
            self.VariableListContent.layout().removeWidget(child)
            child.deleteLater()
        self.set_content_state(False)
        self.set_create_project_button_state(False)
        self.set_edit_template_button_state(False)
        if not keep_selection:
            self.TemplateListView.blockSignals(True)
            self.TemplateListView.currentItem().setSelected(False)
            self.TemplateListView.blockSignals(False)
        self.VariableListHeader.hide()
        self.update_tree_view()

    def create_template(self):
        self.set_app_state(False)
        val = CreateTemplate().exec()
        if val is not None:
            xd = templatoron.TemplatoronObject.from_file(val)
            self.scan_files()
            iterator = QTreeWidgetItemIterator(self.TemplateListView)
            while iterator.value():
                item = iterator.value()
                if isinstance(item, TemplateItem):
                    if item.Template.filename == xd.filename:
                        self.TemplateListView.setCurrentItem(item)
                        break
                iterator += 1
        self.set_app_state(True)

    def scan_files(self):
        self.TemplateListView.clear()
        categories, files = [], []
        f = QFont()
        f.setBold(True)
        for a in os.listdir(self.TEMPLATES_FOLDER):
            pth = os.path.abspath(os.path.join(self.TEMPLATES_FOLDER, a))
            if os.path.exists(pth):
                if os.path.isfile(pth):
                    item = TemplateItem(pth)
                    files.append(item)
                elif os.path.isdir(pth):
                    ctgname = os.path.basename(pth)
                    cat = QTreeWidgetItem([ctgname])
                    cat.setFont(0, f)
                    categories.append(cat)
                    for i in os.listdir(pth):
                        incatpath = os.path.join(pth, i)
                        if os.path.isfile(incatpath):
                            cat.addChild(TemplateItem(incatpath))

        self.TemplateListView.addTopLevelItems(sorted(categories, key=lambda x: x.text(0)))
        self.TemplateListView.addTopLevelItems(sorted(files, key=lambda x: x.text(0)))
        for i in range(self.TemplateListView.topLevelItemCount()):
            self.TemplateListView.topLevelItem(i).sortChildren(0, Qt.SortOrder.AscendingOrder)
        self.TemplateListView.expandAll()

    def templateTreeContextMenu(self, pos):
        index = self.TemplateListView.indexAt(pos)
        if not index.isValid():
            return
        item = self.TemplateListView.itemAt(pos)
        if not isinstance(item, TemplateItem):
            return
        name = item.text(0)
        menu = QMenu()
        menu.addAction("Edit")
        menu.addAction("Remove")
        menu.setStyleSheet("""
        QMenu {
            background-color: #292929;
            font: 15pt "Inter";
            color: white;
            border: 1px solid #444;
            border-radius: 15px;
            padding: 10px;
        }
        QMenu::item {
            padding: 2px 25px 2px 20px;
            border: 1px solid transparent;
            border-radius: 5px;
        }
        QMenu::item:selected {
            background: #333;
            border: 1px solid #666;
        }
        QMenu::item:pressed {
            background: #444;
            border: 1px solid #666;
        }
        """)

        menu.exec_(self.TemplateListView.mapToGlobal(pos))

    def edit_template(self):
        if not self.is_template_selected():
            return
        self.set_app_state(False)
        TemplatoronEditWindow().exec()
        self.set_app_state(True)

    # ===================================================================================
    # STATES CHANGES
    # ===================================================================================

    def set_content_state(self, state: bool):
        opacity_effect = QGraphicsOpacityEffect()
        opacity_effect.setOpacity(0.5)
        self.MainFrame.setGraphicsEffect(None if state else opacity_effect)
        self.MainFrame.setToolTip(None if state else "Firstly select template at the left panel.")
        self.MainContentFrame.setEnabled(state)
        self.MainFrame.setCursor(QCursor(Qt.ArrowCursor if state else Qt.ForbiddenCursor))

    def set_create_project_button_state(self, state: bool):
        opacity_effect = QGraphicsOpacityEffect()
        opacity_effect.setOpacity(0.5)
        self.CreateProjectBtn.setGraphicsEffect(None if state else opacity_effect)
        self.CreateProjectBtn.setCursor(QCursor(Qt.PointingHandCursor if state else Qt.ForbiddenCursor))
        self.CreateProjectBtn.setToolTip(None if state else "You need to enter all parameters before creation.")

    def set_edit_template_button_state(self, state: bool):
        opacity_effect = QGraphicsOpacityEffect()
        opacity_effect.setOpacity(0.5)
        self.EditTemplateBtn.setGraphicsEffect(None if state else opacity_effect)
        self.EditTemplateBtn.setCursor(QCursor(Qt.PointingHandCursor if state else Qt.ForbiddenCursor))
        self.EditTemplateBtn.setToolTip(None if state else "You need to select some template to be able to edit it!")

    def set_app_state(self, state: bool):
        opacity_effect = QGraphicsOpacityEffect()
        opacity_effect.setOpacity(0.5)
        self.TemplateListFrame.setGraphicsEffect(None if state else opacity_effect)
        self.TemplateListFrame.setEnabled(state)
        self.setCursor(QCursor(Qt.ArrowCursor if state else Qt.ForbiddenCursor))
        self.set_content_state(state if not state else self.is_template_selected())
