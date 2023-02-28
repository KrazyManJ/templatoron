import ctypes
import json
import os.path

import pyvscode  # type: ignore
from showinfm import show_in_file_manager
from PyQt5 import uic, QtGui
from PyQt5.QtCore import Qt, QProcess, QEventLoop
from PyQt5.QtGui import QCursor, QIcon
from PyQt5.QtWidgets import *
from qframelesswindow import FramelessWindow

from app.components.consolewindow import ConsoleWindow
from app.components.templateitem import TemplateItem
from app.components.titlebar import TitleBar
from app.components.variableinput import VariableInput
from app.src import templatoron, git, utils, dialog, systemsupport
from app.src.filelogger import FileLogger, LogType
from app.src.jetbrains_ides import IDEs, open_file_in_ide, is_ide_installed
from app.src.templatoron import TemplatoronResponse


class TemplatoronWindow(FramelessWindow):
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
    TemplateListView: QListWidget
    DirectoryDisplay: QTreeWidget
    VariableListContent: QWidget
    TemplateLabel: QLabel
    DirectoryDisplayLabel: QLabel
    VariableListLabel: QLabel

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
        self.app = app
        uic.loadUi(os.path.join(__file__, os.path.pardir, "design", "main_window.ui"), self)
        self.setTitleBar(TitleBar(self))
        self.shadowEngine()
        utils.center_widget(self.app, self)
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("me.KrazyManJ.Templatoron.1.0.0")
        for name, icon, pred in self.COMBO_DATA:
            if pred():
                self.ComboOpenVia.addItem(QIcon(f":/open_via/open_icons/{icon}.svg"), name)
        self.connector()
        self.loadConfiguration()
        for font in ["inter.ttf", "firacode.ttf"]:
            QtGui.QFontDatabase.addApplicationFont(os.path.join(__file__, os.path.pardir, "fonts", font))
        for a in os.listdir(self.TEMPLATES_FOLDER):
            self.TemplateListView.addItem(TemplateItem(os.path.abspath(os.path.join(self.TEMPLATES_FOLDER, a))))
        (self.TemplateListView.hide if len(
            os.listdir(self.TEMPLATES_FOLDER)) == 0 else self.NoTemplatesFoundLabel.hide)()
        self.set_content_state(False)
        self.VariableListLabel.hide()
        self.CheckCloseApp.setIcon(QIcon(":/titlebar/x.svg"))
        self.CheckInitGit.setIcon(QIcon(":/content/github.svg"))

        if not git.is_installed(): self.CheckInitGit.hide()

    def connector(self):
        self.OutputPathButton.clicked.connect(self.change_path)  # type: ignore
        self.CreateProjectBtn.clicked.connect(self.create_project)  # type: ignore
        self.TemplateListView.itemSelectionChanged.connect(self.handle_item_selection_changed)  # type: ignore
        self.ComboOpenVia.currentTextChanged.connect(self.settingPropertyChanged)  # type: ignore
        self.CheckCloseApp.stateChanged.connect(self.settingPropertyChanged)  # type: ignore
        self.CheckInitGit.stateChanged.connect(self.settingPropertyChanged)  # type: ignore

    def shadowEngine(self):
        utils.apply_shadow(self.TemplateLabel, 20, r=30)
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

    def saveConfiguration(self):
        json.dump({"output_path": self.OutputPathInput.text(), "close_app": self.CheckCloseApp.isChecked(),
                   "init_git": self.CheckInitGit.isChecked(), "open_via": self.ComboOpenVia.currentText()},
                  open("configuration.json", "w"), indent=4, sort_keys=True)

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
        if not self.is_something_selected():
            return
        if len([i for i in self.get_variables() if i.is_empty()]) > 0:
            return
        temp = self.get_selected().Template
        logger = FileLogger(temp.filename)
        pth = self.OutputPathInput.text()
        logger.log(f'Beginning of creation of project to path "{pth}"')
        if len(temp.commands) > 0:
            if not dialog.Confirm(
                    "This template contains terminal commands to execute after project creation and it can take some time to execute them. Do you want to continue?"):
                logger.log("Declined command warning, terminating project creation")
                logger.save()
                return
        varvals = {i.get_id(): i.get_value() for i in self.get_variables()}
        logger.log("")
        logger.log("Variables: ")
        logger.log("")
        for k, v in varvals.items(): logger.log(f'- {k} = "{v}"')
        logger.log("")
        respath = os.path.join(pth, templatoron.parse_variable_values(list(temp.structure.keys())[0], varvals))
        resallpaths = [os.path.join(pth, templatoron.parse_variable_values(a, varvals)) for a in temp.structure.keys()]
        self.set_app_state(False)
        logger.log(f'Attempting to create project from template "{temp.name}"...')

        def log_file_create(file):
            fileType = "directory" if os.path.isdir(file) else "file"
            logger.log(f'Successfully created {fileType} "{file}"')

        response = temp.create_project(self.OutputPathInput.text(), onfilecreate=log_file_create, **varvals)

        for restype, message, logmsg in [(
        TemplatoronResponse.ACCESS_DENIED, "Access denied by operating system while trying to create project!",
        "Creation blocked by OS priviledges"), (
        TemplatoronResponse.ALREADY_EXIST, "There is already existing project with these parameters!",
        "Creation blocked by colision with already existing files")]:
            if response == restype:
                dialog.Warn(message)
                logger.warn(logmsg)
                self.set_app_state(True)
                logger.save()
                return
        logger.log("Successfully created all files!")
        if len(temp.commands) > 0:
            logger.log("Running template commands...")
            logger.log(f'{"=" * 20} CONSOLE OUTPUT {"=" * 20}')
            output = temp.command_path(self.OutputPathInput.text(), **varvals)
            console = ConsoleWindow(temp.commands, output, logger)
            console.exec()
            logger.log(f'{"=" * 20} END OF OUTPUT {"=" * 20}')
        self.set_app_state(True)
        for label, fct in {"File Explorer": lambda: show_in_file_manager(resallpaths, False),
                           "Visual Studio Code": lambda: pyvscode.open_folder(
                               *([pth, resallpaths] if len(resallpaths) > 1 else [respath])),
                           "PyCharm": lambda: open_file_in_ide(IDEs.PYCHARM, resallpaths),
                           "IntelliJ IDEA": lambda: open_file_in_ide(IDEs.INTELLIJ, resallpaths),
                           "PhpStorm": lambda: open_file_in_ide(IDEs.PHPSTORM, resallpaths)}.items():
            if self.ComboOpenVia.currentText() == label:
                fct()
                logger.log(f'Opened project via option "{label}"')
                break

        if self.CheckInitGit.isChecked():
            gitpth = pth if len(resallpaths) > 1 or os.path.isfile(respath) else respath
            if not git.already_init(gitpth):
                git.init(gitpth)
                logger.log("Git has been successfully initialized")
            else:
                logger.warn("Git is already initialized, skipping")
                dialog.Warn("Git repository in this folder is already initialized, skipped initializing!")
        else:
            logger.log("Git init is not enabled, ignoring")

        if self.CheckCloseApp.isChecked():
            self.saveConfiguration()
            logger.log("Closing app")
            logger.save()
            self.close()
        else:
            logger.log("App closing is not enabled, ignoring closing")
            logger.save()

    def run_command(self, command, work_directory):

        process = QProcess()
        if work_directory is not None:
            process.setWorkingDirectory(work_directory)
        process.start(command)

        def end():
            loop.quit()
            print(process.exitCode())
            dialog.Info("Successfully created project!")
            self.set_app_state(True)

        loop = QEventLoop()
        process.finished.connect(end)  # type: ignore
        loop.exec_()

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
                VariableInput(self, var["id"], var["displayname"], file_mask=mask))
        if self.VariableListContent.layout().count() == 0:
            self.VariableListLabel.hide()
            self.set_create_button_state(True)
        else:
            self.VariableListLabel.show()
            self.set_create_button_state(len([i for i in self.get_variables() if i.is_empty()]) == 0)
        self.update_tree_view()

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

    def set_create_button_state(self, state: bool):
        opacity_effect = QGraphicsOpacityEffect()
        opacity_effect.setOpacity(0.5)
        self.CreateProjectBtn.setGraphicsEffect(None if state else opacity_effect)
        self.CreateProjectBtn.setCursor(QCursor(Qt.PointingHandCursor if state else Qt.ForbiddenCursor))
        self.CreateProjectBtn.setToolTip(None if state else "You need to enter all parameters before creation.")

    def set_app_state(self, state: bool):
        opacity_effect = QGraphicsOpacityEffect()
        opacity_effect.setOpacity(0.5)
        self.TemplateListFrame.setGraphicsEffect(None if state else opacity_effect)
        self.TemplateListFrame.setEnabled(state)
        self.setCursor(QCursor(Qt.ArrowCursor if state else Qt.ForbiddenCursor))
        self.set_content_state(state)
