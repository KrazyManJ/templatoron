import os.path

import pyvscode  # type: ignore
from PyQt5 import uic, QtGui
from PyQt5.QtCore import Qt, QItemSelection
from PyQt5.QtGui import QCursor, QIcon, QFont
from PyQt5.QtWidgets import *
from qframelesswindow import FramelessWindow

from app.components.templateitem import TemplateItem
from app.components.titlebar import TitleBar
from app.components.variableinput import VariableInput
from app.components.windows.console import ConsoleWindow
from app.components.windows.createtemplate import CreateTemplate
from app.components.windows.defaultvar import DefaultVariableWindow
from app.design import styleconstants
from app.editwindow import TemplatoronEditWindow
from app.src import templatoron, git, utils, dialog, pather, configuration, openvia
from app.src.templatoron import TemplatoronResponse


class TemplatoronMainWindow(FramelessWindow):
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

    # ===================================================================================
    # INIT
    # ===================================================================================

    def __init__(self, app: QApplication):
        super().__init__()
        self.defaultVarValues = {}
        uic.loadUi(pather.design_file("main_window.ui"), self)
        self.setTitleBar(TitleBar(self))
        self.shadowEngine()
        utils.center_widget(QApplication.instance(), self)
        for name, icon, pred in openvia.CHECK_DATA:
            if pred():
                self.ComboOpenVia.addItem(QIcon(f":/open_via/open_icons/{icon}.svg"), name)
        self.loadConfiguration()
        self.connector()
        self.update_template_list()
        self.set_content_state(False)
        self.set_create_project_button_state(False)
        self.set_edit_template_button_state(False)
        self.VariableListHeader.hide()
        self.CheckCloseApp.setIcon(QIcon(":/titlebar/titlebar/close.svg"))
        self.CheckInitGit.setIcon(QIcon(":/content/github.svg"))
        if not git.is_installed(): self.CheckInitGit.hide()
        self.TemplateListView.setContextMenuPolicy(Qt.CustomContextMenu)
        self.TemplateLabel.setFocus()

    def mousePressEvent(self, a0: QtGui.QMouseEvent) -> None:
        self.clearFocus()

    def connector(self):
        self.CreateTemplateBtn.clicked.connect(self.create_template)  # type: ignore
        self.OutputPathButton.clicked.connect(self.change_path)  # type: ignore
        self.CreateProjectBtn.clicked.connect(self.create_project)  # type: ignore
        self.TemplateListView.selectionChanged = self.handle_item_selection_changed  # type: ignore
        self.ComboOpenVia.currentTextChanged.connect(self.settingPropertyChanged)  # type: ignore
        self.CheckCloseApp.stateChanged.connect(self.settingPropertyChanged)  # type: ignore
        self.CheckInitGit.stateChanged.connect(self.settingPropertyChanged)  # type: ignore
        self.DefaultValuesBtn.clicked.connect(self.setDefaultParameters)  # type: ignore
        self.TemplateListView.customContextMenuRequested.connect(self.templateTreeContextMenu)  # type: ignore
        self.TemplateListView.mouseMoveEvent = lambda ev: None  # Disables mouse drag selecting (causes crash)
        self.EditTemplateBtn.clicked.connect(self.edit_template)  # type: ignore

    def shadowEngine(self):
        utils.apply_shadow(self.TemplateLabel, 150, r=30)
        utils.apply_shadow(self.DirectoryDisplayLabel, 40)
        utils.apply_shadow(self.VariableListLabel, 40)
        utils.apply_shadow(self.CreateProjectBtn, 40)

    # ===================================================================================
    # CONFIGURATION LOADER/SAVER
    # ===================================================================================

    def loadConfiguration(self):
        data: dict = configuration.load()
        self.OutputPathInput.setText(data["output_path"])
        self.CheckCloseApp.setChecked(data["close_app"])
        self.CheckInitGit.setChecked(data["init_git"])
        self.ComboOpenVia.setCurrentText(data["open_via"])
        self.defaultVarValues = data["default_var_values"]

    def saveConfiguration(self):
        configuration.save({
            "output_path": self.OutputPathInput.text(),
            "close_app": self.CheckCloseApp.isChecked(),
            "init_git": self.CheckInitGit.isChecked(),
            "open_via": self.ComboOpenVia.currentText(),
            "default_var_values": self.defaultVarValues
        })

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
            (TemplatoronResponse.ACCESS_DENIED, "Access denied by operating system while trying to create project!"),
            (TemplatoronResponse.ALREADY_EXIST, "There is already existing project with these parameters!")]:
            if response == restype:
                dialog.Warn(message)
                self.set_app_state(True)
                return
        if len(temp.commands) > 0:
            ConsoleWindow(temp.commands, temp.command_path(self.OutputPathInput.text(), **varvals)).exec()
        self.set_app_state(True)
        for label, fct in openvia.OPEN_DATA.items():
            if self.ComboOpenVia.currentText() == label:
                fct(pth, respath, resallpaths)
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
        return len([a for a in self.TemplateListView.selectedItems() if isinstance(a, TemplateItem)]) == 1

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
            created = templatoron.TemplatoronObject.from_file(val)
            self.update_template_list()
            iterator = QTreeWidgetItemIterator(self.TemplateListView)
            while iterator.value():
                item = iterator.value()
                if isinstance(item, TemplateItem):
                    if os.path.abspath(item.path) == os.path.abspath(val):
                        self.TemplateListView.setCurrentItem(item)
                        break
                iterator += 1
        self.set_app_state(True)

    def update_template_list(self):
        if len(os.listdir(pather.TEMPLATES_FOLDER)) == 0:
            self.TemplateListView.hide()
            self.NoTemplatesFoundLabel.show()
            return
        self.TemplateListView.show()
        self.NoTemplatesFoundLabel.hide()
        self.TemplateListView.clear()
        categories, files = [], []
        f = QFont()
        f.setBold(True)
        for p in pather.listdirfullpath(pather.TEMPLATES_FOLDER):
            pth = os.path.abspath(p)
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
        menu.addAction("Edit", lambda: self.edit_template())
        menu.addAction("Remove", lambda: self.remove_template(item))  # type: ignore
        menu.setStyleSheet(styleconstants.QMENU)
        menu.exec(self.TemplateListView.mapToGlobal(pos))

    def remove_template(self, item):
        if not dialog.Confirm(f'Are you sure you want to remove template "{item.Template.name}"?'):
            return
        if self.get_selected() == item:
            self.unselect_template()
        item.remove()
        index = self.TemplateListView.indexOfTopLevelItem(item)
        if index == -1:
            item.parent().removeChild(item)
        else:
            self.TemplateListView.takeTopLevelItem(index)

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
