# QRC Editor
#
# Copyright 2020 Simone <sanfe75@gmail.com>
#
# Licensed under the Apache License, Version 2.0(the "License"); you may not use this file except
# in compliance with the License.You may obtain a copy of the License at:
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software distributed under the License is distributed
# on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License
# for the specific language governing permissions and limitations under the License.
#

import os
import platform
import subprocess
import sys
import PySide6

from PySide6.QtCore import QSettings, Qt
from PySide6.QtGui import QAction, QIcon, QKeySequence, QShortcut
from PySide6.QtWidgets import QApplication, QFileDialog, QMainWindow, QMessageBox, QTableWidget, QTableWidgetItem,\
    QTabWidget

import qrcdata
import qrcdlg
import qrcresources

__version__ = "0.8.1"


class QrcEditor(QMainWindow):
    """Create a QRC Editor main window application.
    """

    next_id = 1
    instances = []

    def __init__(self, file_name=None, parent=None):
        """Constructor for QrcEditor class.
        """

        super(QrcEditor, self).__init__(parent)
        self.setAttribute(Qt.WA_DeleteOnClose)
        QrcEditor.instances.append(self)

        self.collection = qrcdata.ResourceCollection()

        if file_name is None:
            self.collection.set_file_name("Unnamed-{0}".format(QrcEditor.next_id))
            QrcEditor.next_id += 1
            self.collection.set_dirty(False)
        else:
            _, message = self.collection.load(file_name)
            self.statusBar().showMessage(message, 5000)

        self.options = {"program": "pyside6-rcc.exe",
                        "no_compress": False,
                        "compress": False,
                        "compress_level": 1,
                        "threshold": False,
                        "threshold_level": 70}
        self.help_message = ""
        self.rcc_version = None
        self.central_widget = QTabWidget()
        self.setCentralWidget(self.central_widget)

        self.statusBar().setSizeGripEnabled(False)
        self.statusBar().showMessage("Ready", 5000)

        self.file_compile_action = self.create_action("&Compile", self.file_compile, "Alt+C",
                                                      "file_compile", "Compile a Resource collection")
        file_new_action = self.create_action("&New...", self.file_new, QKeySequence.New,
                                             "file_new", "Create a Resource collection file")
        file_open_action = self.create_action("&Open...", self.file_open, QKeySequence.Open,
                                              "file_open", "Open a Resource collection file")
        file_save_action = self.create_action("&Save", self.file_save, QKeySequence.Save,
                                              "file_save", "Save the Resource collection file")
        file_save_all_action = self.create_action("Save A&ll", self.file_save_all, icon="file_save_all",
                                                  tip="Save all the Resource collections")
        file_save_as_action = self.create_action("&Save as...", self.file_save_as, QKeySequence.SaveAs,
                                                 "file_save_as", "Save the Resource collection using a new name")
        file_close_action = self.create_action("&Close", self.close, QKeySequence.Close,
                                               "file_close", "Close this editor")
        file_quit_action = self.create_action("&Quit", self.file_quit, "Ctrl+Q",
                                              "file_quit", "Close the application")
        self.edit_add_resource_action = self.create_action("&Add Resource...", self.edit_add_resource, "Ctrl+A",
                                                           "edit_add_resource", "Add a resource")
        self.edit_copy_action = self.create_action("Copy", self.edit_copy, QKeySequence.Copy, "edit_copy",
                                                   "Copy selected resources")
        self.edit_cut_action = self.create_action("Cut", self.edit_cut, QKeySequence.Cut, "edit_cut",
                                                  "Cut selected resources")
        self.edit_edit_resource_action = self.create_action("&Edit Resource...", self.edit_edit_resource, "Ctrl+E",
                                                            "edit_edit_resource", "Edit the selected resource")
        self.edit_paste_action = self.create_action("Paste", self.edit_paste, QKeySequence.Paste, "edit_paste",
                                                    "Paste resource")
        self.edit_remove_resource_action = self.create_action("&Remove Resource", self.edit_remove_resource,
                                                              QKeySequence.Delete,
                                                              "edit_delete_resource", "Remove the selected resource")
        self.edit_add_tab_action = self.create_action("&Add Tab...", self.edit_add_tab, "Alt+A",
                                                      "edit_add_tab", "Add a tab")
        self.edit_edit_tab_action = self.create_action("&Edit Tab...", self.edit_edit_tab, "Alt+E",
                                                       "edit_edit_tab", "Edit the current tab")
        self.edit_remove_tab_action = self.create_action("&Remove Tab", self.edit_remove_tab, None,
                                                         "edit_delete_tab", "Remove the current tab")
        self.edit_move_up_action = self.create_action("Move &Up", self.edit_move_up, QKeySequence.MoveToNextLine,
                                                      "edit_move_up", "Move the resource up")
        self.edit_move_down_action = self.create_action("Move &Down", self.edit_move_down,
                                                        QKeySequence.MoveToPreviousLine, "edit_move_down",
                                                        "Move the resource down")
        self.edit_move_left_action = self.create_action("Move &Left", self.edit_move_left,
                                                        QKeySequence.MoveToPreviousPage, "edit_move_left",
                                                        "Move the resources to the left")
        self.edit_move_right_action = self.create_action("Move &Right", self.edit_move_right,
                                                         QKeySequence.MoveToNextPage, "edit_move_right",
                                                         "Move the resources to the right")
        self.edit_sort_action = self.create_action("&Sort...", self.edit_sort, "Ctrl+S",
                                                   "edit_sort", "Sort the resource table")
        self.edit_update_action = self.create_action("&Update", self.edit_update, QKeySequence.Refresh,
                                                     "edit_update", "Update the resource table")
        edit_settings_action = self.create_action("&Settings...", self.edit_settings, "Ctrl+I", "edit_settings")
        self.window_arrange_horizontal_action = self.create_action("Tile &Horizontally",
                                                                   self.window_arrange_horizontal,
                                                                   "Alt+H", "window_arrange_horizontal",
                                                                   "Arrange the windows horizontally")
        self.window_arrange_vertical_action = self.create_action("Tile &Vertically", self.window_arrange_vertical,
                                                                 "Alt+V", "window_arrange_vertical",
                                                                 "Arrange the windows vertically")
        help_about_action = self.create_action("&About QRC Editor", self.help_about)

        file_menu = self.menuBar().addMenu("&File")
        self.add_actions(file_menu, (file_new_action, file_open_action, file_save_action, file_save_all_action,
                                     file_save_as_action, None, self.file_compile_action, None, file_close_action,
                                     file_quit_action))
        edit_menu = self.menuBar().addMenu("&Edit")
        self.add_actions(edit_menu, (self.edit_paste_action, self.edit_copy_action, self.edit_cut_action, None,
                                     self.edit_add_resource_action, self.edit_edit_resource_action,
                                     self.edit_remove_resource_action, self.edit_move_up_action,
                                     self.edit_move_down_action, self.edit_sort_action, None, self.edit_add_tab_action,
                                     self.edit_edit_tab_action, self.edit_remove_tab_action, self.edit_move_left_action,
                                     self.edit_move_right_action, None, self.edit_update_action, None,
                                     edit_settings_action))

        self.window_menu = self.menuBar().addMenu("&Window")

        help_menu = self.menuBar().addMenu("&Help")
        help_menu.addAction(help_about_action)

        file_toolbar = self.addToolBar("File")
        file_toolbar.setObjectName("FileToolbar")
        self.add_actions(file_toolbar, (file_new_action, file_open_action, file_save_action, None,
                                        self.file_compile_action))
        edit_toolbar = self.addToolBar("Edit")
        edit_toolbar.setObjectName("EditToolbar")
        self.add_actions(edit_toolbar, (self.edit_add_resource_action, self.edit_edit_resource_action,
                                        self.edit_remove_resource_action, self.edit_move_up_action,
                                        self.edit_move_down_action, self.edit_sort_action, None,
                                        self.edit_add_tab_action, self.edit_edit_tab_action, self.edit_move_left_action,
                                        self.edit_move_right_action, None, self.edit_update_action))
        file_toolbar.setObjectName("EditToolbar")

        self.central_widget.setTabsClosable(True)
        self.central_widget.tabCloseRequested.connect(self.edit_remove_tab)
        self.central_widget.currentChanged.connect(self.update_ui)
        self.window_menu.aboutToShow.connect(self.update_window_menu)
        QApplication.clipboard().dataChanged.connect(self.check_clipboard)

        self.check_clipboard()
        self.load_settings()
        self.update_widget()
        self.update_ui()

    @staticmethod
    def add_actions(target, actions):
        """Add the given actions to the target.

        Add the given actions to the target, the actions are a list or tuple, if an element is None
        the function add a separator to the target.

        Parameters:
        target (object): the target of the add_actions
        actions (list): the list of actions to add
        """

        for action in actions:
            if action is None:
                target.addSeparator()
            else:
                target.addAction(action)

    @staticmethod
    def is_open(file_name):
        """Check if an editor with file_name collection is open.

        If an editor with file_name collection is open the method shows the existing window, otherwise returns False
        """

        for editor in QrcEditor.instances:
            if editor.collection.file_name() == file_name:
                editor.activateWindow()
                editor.raise_()
                return True
        return False

    def check_clipboard(self):
        """Check if it is possible to paste the content of the clipboard.
        """

        data = QApplication.clipboard().mimeData()
        if not data.hasText():
            self.edit_paste_action.setEnabled(False)
        else:
            enable = True
            new_resources = [resource.split("\t") for resource in data.text().strip().split("\n")]
            for resource in new_resources:
                if len(resource) > 2:
                    enable = False
                    break
                file_name = resource[-1]

                if not self.check_file(file_name):
                    enable = False
                    break
            self.edit_paste_action.setEnabled(enable)

    def check_file(self, file_name):
        """Check if file_name is a valid file and if it is in a subdirectory of the present working directory.
        """

        pwd = os.path.realpath(os.path.dirname(self.collection.file_name()))
        if file_name.startswith("file:///"):
            file_name = file_name[len("file:///"):]
        else:
            file_name = os.path.join(pwd, file_name)

        if os.path.isfile(file_name) and pwd == os.path.commonpath([file_name, pwd]):
            return True
        return False

    def check_program(self, program):
        """Check the program used to compile the .qrc file.
        """

        try:
            completed = subprocess.run([program, "-help"], capture_output=True)
        except (IOError, OSError, subprocess.CalledProcessError):
            return False
        if completed and completed.returncode == 0:
            self.help_message = completed.stdout.decode("UTF-8")
            try:
                completed = subprocess.run([program, "-version"], capture_output=True)
            except (IOError, OSError, subprocess.CalledProcessError):
                self.rcc_version = None
            self.rcc_version = completed.stdout.decode("UTF-8")
            return True
        return False

    def closeEvent(self, event):
        """Close the window, save application state.
        """

        if self.ok_to_continue():
            settings = QSettings()
            settings.setValue("Geometry", self.saveGeometry())
            settings.setValue("MainWindow/State", self.saveState())
            settings.setValue("Options/Program", self.options["program"])
            settings.setValue("Options/NoCompress", self.options["no_compress"])
            settings.setValue("Options/Compress", self.options["compress"])
            settings.setValue("Options/CompressLevel", self.options["compress_level"])
            settings.setValue("Options/Threshold", self.options["threshold"])
            settings.setValue("Options/ThresholdLevel", self.options["threshold_level"])
            QrcEditor.instances.remove(self)
        else:
            event.ignore()

    def create_action(self, text, slot=None, shortcut=None, icon=None, tip=None, checkable=False, signal="triggered"):
        """Create the actions for the interface.

        Parameters:
        text (str): the name of the action
        slot (func): the slot for the action
        shortcut (str): the shortcut
        icon (str): the icon file name without ext
        tip (str): the tooltip for the action
        checkable (bool): if checkable
        signal (str): the signal type

        Return:
        QAction: the action created
        """

        action = QAction(text, self)
        if icon is not None:
            action.setIcon(QIcon(":/{0}.png".format(icon)))
        if shortcut is not None:
            action.setShortcut(shortcut)
        if tip is not None:
            action.setToolTip(tip)
            action.setStatusTip(tip)
        if slot is not None:
            if signal == "triggered":
                action.triggered.connect(slot)
            if signal == "toggled":
                action.toggled[bool].connect(slot)
        if checkable:
            action.setCheckable(checkable)
        return action

    def ok_to_continue(self):
        """Create Dialog to continue.

        Return:
        bool: it is OK to continue
        """

        if self.collection.dirty():
            reply = QMessageBox.question(self, "QRC Editor - Unsaved Changes", "Save unsaved changes?",
                                         QMessageBox.Yes | QMessageBox.No | QMessageBox.Cancel)
            if reply == QMessageBox.Cancel:
                return False
            elif reply == QMessageBox.Yes:
                result = self.file_save()
                return result
        return True

    def edit_add_resource(self):
        """Add a resource.
        """

        file_dlg = qrcdlg.ResourceFileDlg(self.collection.file_name())
        indexes = []
        row = self.central_widget.currentWidget().currentRow()
        if file_dlg.exec():
            file_names = file_dlg.selectedFiles()
            for index, file_name in enumerate(file_names):
                if not os.path.abspath(file_name).startswith(os.path.abspath(os.path.
                                                             dirname(self.collection.file_name()))):
                    QMessageBox.warning(self, "File Error", "Selected file is not in a subdirectory of {0}"
                                        .format(os.path.basename(self.collection.file_name())))
                    file_names[index] = None
        file_names = [file for file in file_names if file is not None]
        for file_name in file_names:
            dialog = qrcdlg.ResourceDlg(self.collection, self.central_widget.currentIndex(), row, file_name, self)
            row += 1
            indexes.append(row)
            if dialog.exec():
                self.update_table(self.central_widget.currentWidget(), dialog.resources, indexes)
                self.update_ui()
                self.statusBar().showMessage("Resource added", 5000)

    def edit_add_tab(self):
        """Add a tab.
        """

        initial_length = len(self.collection)
        dialog = qrcdlg.TabDlg(self.collection, None, self.central_widget.currentIndex(), self)
        if dialog.exec():
            self.update_widget(dialog.index)
            self.update_ui()
            if len(self.collection) > initial_length:
                self.statusBar().showMessage("Tab added", 5000)
            else:
                self.statusBar().showMessage("Tab already existing", 5000)

    def edit_copy(self):
        """Copy the selected resources to the clipboard.
        """

        table = self.central_widget.currentWidget()
        table_index = self.central_widget.currentIndex()
        resources = self.collection[table_index]
        indexes = [selected.row() for selected in table.selectionModel().selectedRows()]
        text = ""

        for index in indexes:
            alias = resources[index].alias()
            file = resources[index].file()
            line = "{0}\t{1}".format(alias, file) if alias is not None else file
            text += "{0}\n".format(line)

        QApplication.clipboard().setText(text)

    def edit_cut(self):
        """Cut the selected resources to the clipboard.
        """

        self.edit_copy()
        self.edit_remove_resource()

    def edit_edit_resource(self):
        """Edit the selected resource.
        """

        table = self.central_widget.currentWidget()
        table_index = self.central_widget.currentIndex()
        resources = self.collection[table_index]
        indexes = [selected.row() for selected in table.selectionModel().selectedRows()]

        for index in indexes:
            dialog = qrcdlg.ResourceDlg(self.collection, table_index, index, parent=self)
            if dialog.exec():
                self.collection.set_dirty(True)
                self.statusBar().showMessage("Resource edited", 5000)

        self.update_table(table, resources, indexes)
        self.update_ui()

    def edit_edit_tab(self):
        """Edit a tab.
        """

        dialog = qrcdlg.TabDlg(self.collection, self.collection[self.central_widget.currentIndex()], self)
        if dialog.exec():
            self.update_widget(dialog.index)
            self.update_ui()
            self.statusBar().showMessage("Tab edited", 5000)

    def edit_move_down(self):
        """Move the selected resource down one line.
        """

        table = self.central_widget.currentWidget()
        table_index = self.central_widget.currentIndex()
        resources = self.collection[table_index]
        indexes = sorted([selected.row() for selected in table.selectionModel().selectedRows()], reverse=True)
        for index in indexes:
            resources[index], resources[index + 1] = resources[index + 1], resources[index]

        self.collection.set_dirty(True)
        indexes = [index + 1 for index in indexes]
        self.update_table(table, resources, indexes)
        self.update_ui()
        message = "Resource moved" if len(indexes) == 1 else "Resources moved"
        self.statusBar().showMessage(message, 5000)

    def edit_move_left(self):
        """Move the active tab to the left.
        """

        index = self.central_widget.currentIndex()
        self.collection[index - 1], self.collection[index] = self.collection[index], self.collection[index - 1]

        self.collection.set_dirty(True)
        self.update_widget()
        self.central_widget.setCurrentIndex(index - 1)
        self.statusBar().showMessage("Tab moved", 5000)

    def edit_move_right(self):
        """Move the active tab to the right.
        """

        index = self.central_widget.currentIndex()
        self.collection[index + 1], self.collection[index] = self.collection[index], self.collection[index + 1]

        self.collection.set_dirty(True)
        self.update_widget()
        self.central_widget.setCurrentIndex(index + 1)
        self.statusBar().showMessage("Tab moved", 5000)

    def edit_move_up(self):
        """Move the selected resource up one line.
        """

        table = self.central_widget.currentWidget()
        table_index = self.central_widget.currentIndex()
        resources = self.collection[table_index]
        indexes = sorted([selected.row() for selected in table.selectionModel().selectedRows()])
        for index in indexes:
            resources[index - 1], resources[index] = resources[index], resources[index - 1]

        self.collection.set_dirty(True)
        indexes = [index - 1 for index in indexes]
        self.update_table(table, resources, indexes)
        self.update_ui()
        message = "Resource moved" if len(indexes) == 1 else "Resources moved"
        self.statusBar().showMessage(message, 5000)

    def edit_paste(self):
        """Paste the content of the clipboard to the resources.
        """

        table_index = self.central_widget.currentIndex()
        resources = self.collection[table_index]
        new_resources = QApplication.clipboard().text().strip().split("\n")

        indexes = []
        row = self.central_widget.currentWidget().currentRow() + 1
        for data in new_resources:
            data = data.split("\t")
            if len(data) == 1:
                if data[0].startswith("file:///"):
                    file = data[0][len("file:///") + len(os.path.dirname(self.collection.file_name())):]
                else:
                    file = data[0]
                resource = qrcdata.Resource(file)
            else:
                resource = qrcdata.Resource(data[1], data[0])
            resources.insert(row, resource)
            indexes.append(row)
            row += 1

        self.update_table(self.central_widget.currentWidget(), self.collection[table_index], indexes)
        self.collection.set_dirty(True)
        self.update_ui()
        self.statusBar().showMessage("Clipboard pasted", 5000)

    def edit_remove_resource(self):
        """Remove the selected resource.
        """

        table = self.central_widget.currentWidget()
        table_index = self.central_widget.currentIndex()
        resources = self.collection[table_index]
        indexes = sorted([selected.row() for selected in table.selectionModel().selectedRows()], reverse=True)
        message = "Resources removed" if len(indexes) > 1 else "Resource removed"

        for index in indexes:
            resources.pop(index)
        self.collection.set_dirty(True)
        self.update_table(table, resources)
        self.update_ui()
        self.statusBar().showMessage(message, 5000)

    def edit_remove_tab(self, index=-1):
        """remove a tab.

        Parameters:
        index (int) the index of the tab to close, current tab closed if index = -1
        """

        if index >= 0:
            self.central_widget.setCurrentIndex(index)
        reply = QMessageBox.question(self, "QRC Editor - Remove Tab", "Remove the tab and all its resources?",
                                     QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            self.collection.pop(self.central_widget.currentIndex())
            self.collection.set_dirty(True)
            self.update_widget()
            self.statusBar().showMessage("Tab removed", 5000)

    def edit_settings(self):
        """Open the settings dialog.
        """

        dialog = qrcdlg.ResourceSettingsDlg(self.options, self)
        if dialog.exec():
            self.statusBar().showMessage("Settings updated", 5000)

    def edit_sort(self):
        """Open the sort dialog.
        """

        dialog = qrcdlg.TabSortDlg(self)
        if dialog.exec():
            table = self.central_widget.currentWidget()
            table_index = self.central_widget.currentIndex()
            resources = self.collection[table_index]
            indexes = [selected.row() for selected in table.selectionModel().selectedRows()]
            selected_resources = [resources[index] for index in indexes]
            if dialog.key_combo_box.currentIndex() == 0:
                resources.sort(key=lambda resource: [resource.alias(), resource.file()],
                               reverse=dialog.reverse_checkbox.isChecked())
            else:
                resources.sort(key=lambda resource: [resource.file(), resource.alias()],
                               reverse=dialog.reverse_checkbox.isChecked())
            self.collection.set_dirty(True)
            indexes = [resources.index(resource) for resource in selected_resources]
            self.update_table(table, resources, indexes)
            self.update_ui()
            self.statusBar().showMessage("Table updated", 5000)

    def edit_update(self):
        """Update the table.
        """

        table = self.central_widget.currentWidget()
        table_index = self.central_widget.currentIndex()
        resources = self.collection[table_index]
        indexes = [selected.row() for selected in table.selectionModel().selectedRows()]

        self.update_table(table, resources, indexes)
        self.update_ui()
        self.statusBar().showMessage("Table updated", 5000)

    def file_compile(self):
        """Compile a resource collection to a .py file.
        """

        if not self.ok_to_continue():
            return

        file_name = self.collection.file_name()[:-4] + ".py"
        file_name, _ = QFileDialog.getSaveFileName(self, "QRC Editor - Compile Resource Collection File",
                                                   file_name, "Python file (*.py)")
        if file_name:
            options = [self.options["program"], "-o", file_name]
            if self.options["no_compress"]:
                options.append("-no-compress")
            if self.options["compress"]:
                options.extend(["-compress", "{0}".format(self.options["compress_level"])])
            if self.options["threshold"]:
                options.extend(["-threshold", "{0}".format(self.options["threshold_level"])])

            options.append(self.collection.file_name())
            completed = None
            try:
                completed = subprocess.run(options, check=True)
            except (IOError, OSError, subprocess.CalledProcessError) as err:
                QMessageBox.critical(self, "Compile Error", "There was an error during the process: {0}".format(err))
            if completed and completed.returncode == 0:
                self.statusBar().showMessage("{0} successfully compiled".format(os.path.basename(file_name)), 5000)

    def file_new(self):
        """Create a new file.
        """

        file_name, _ = QFileDialog.getSaveFileName(self, "QRC Editor - Save Resource Collection File",
                                                   ".", "Resource Collection file (*.qrc)")
        if file_name:
            if file_name[-4:].lower() != ".qrc":
                file_name += ".qrc"
            if not self.collection.dirty() and self.collection.file_name().startswith("Unnamed"):
                self.collection.set_file_name(file_name)
                self.update_ui()
            else:
                QrcEditor(file_name).show()

    def file_open(self):
        """Create the dialog to select and then open a qrc file.
        """

        file_dir = os.path.dirname(self.collection.file_name())\
            if self.collection.file_name() is not None else "."
        file_name, _ = QFileDialog.getOpenFileName(self, "QRC Editor - Load Resource Collection File",
                                                   file_dir, "Resource Collection file (*.qrc)")
        if file_name:
            if file_name[-4:].lower() != ".qrc":
                file_name += ".qrc"

            if not self.is_open(file_name):
                if not self.collection.dirty() and self.collection.file_name().startswith("Unnamed"):
                    _, message = self.collection.load(file_name)
                    self.statusBar().showMessage(message, 5000)
                else:
                    QrcEditor(file_name).show()
                self.update_widget()
                self.update_ui()

    @staticmethod
    def file_quit():
        """Close all the files and exit the application.
        """

        QApplication.closeAllWindows()

    def file_save(self):
        """Save a file.
        """

        if self.collection.file_name().startswith("Unnamed"):
            self.file_save_as()
        else:
            result, message = self.collection.save()
            self.statusBar().showMessage(message, 5000)
            self.update_ui()
            return result

    def file_save_all(self):
        """Save all the files.
        """

        count = 0
        for editor in QrcEditor.instances:
            if editor.collection.dirty():
                ok, message = editor.collection.save()
                if ok:
                    count += 1
                    self.statusBar().showMessage(message, 5000)
        self.statusBar().showMessage("Saved {0} of {1} files".format(count, len(QrcEditor.instances)), 5000)
        self.update_ui()

    def file_save_as(self):
        """Create the dialog to save a new file.
        """

        file_name = self.collection.file_name() if self.collection.file_name() else "."
        file_name, _ = QFileDialog.getSaveFileName(self, "QRC Editor - Save Resource Collection File",
                                                   file_name, "Resource Collection file (*.qrc)")
        if file_name:
            if file_name[-4:].lower() != ".qrc":
                file_name += ".qrc"
            result, message = self.collection.save(file_name)
            self.statusBar().showMessage(message, 5000)
            self.update_widget(self.central_widget.currentIndex())
            self.update_ui()
            return result

    def help_about(self):
        """Open the about message.
        """

        message = """<b>QRC Editor</b> v {0}
                     <p>Copyright &copy; Sanfe Ltd.
                     All rights reserved.
                     <p>This application can be used to create and
                     compile a resource collection file that can
                     be used in in python pyside6 projects.
                     <p> Python {1} - Qt {2} - PySide6 {3}
                     """.format(__version__, platform.python_version(), PySide6.QtCore.__version__, PySide6.__version__)

        if self.rcc_version is not None:
            message += " - {0}".format(self.rcc_version)
        message += " on {0}.<p> Icons by <a href='https://icons8.com'>Icons8</a>".format(platform.system())
        QMessageBox.about(self, "About QRC Editor", message)

    def load_settings(self):
        """Load settings for the application.
        """

        settings = QSettings()
        if (geometry := settings.value("Geometry")) is not None:
            self.restoreGeometry(geometry)
        if (state := settings.value("MainWindow/State")) is not None:
            self.restoreState(state)
        if (program := settings.value("Options/Program")) and self.check_program(program):
            self.options["program"] = program
        else:
            self.options["program"] = "pyside6-rcc.exe"
        if (no_compress := settings.value("Options/NoCompress")) is not None:
            self.options["no_compress"] = True if no_compress == "true" else False
        if (compress := settings.value("Options/Compress")) is not None:
            self.options["compress"] = True if compress == "true" else False
        if (compress_level := settings.value("Options/CompressLevel")) is not None:
            self.options["compress_level"] = int(compress_level)
        if (threshold := settings.value("Options/Threshold")) is not None:
            self.options["threshold"] = True if threshold == "true" else False
        if (threshold_level := settings.value("Options/ThresholdLevel")) is not None:
            self.options["threshold_level"] = int(threshold_level)

    def raise_window(self):
        """Raise and make active editor_to_rise
        """

        title = self.sender().text().split(maxsplit=1)[1]
        for editor in QrcEditor.instances:
            if editor.windowTitle()[:-3] == title:
                editor.activateWindow()
                editor.raise_()
                break

    def update_table(self, table, resources, current_indexes=[]):
        """Create a table and populate it.

        Parameters:
        table (QTabWidget): the table to populate
        resources: the resources used to populate the table
        current_indexes: the list of indexes of the current resources, to keep the correct resource selected

        Return:
        QTabWidget: the populated table
        """

        table.clearSelection()
        table.setRowCount(len(resources))
        table.setColumnCount(2)
        table.setHorizontalHeaderLabels(["Alias", "File"])
        table.setAlternatingRowColors(True)
        table.setEditTriggers(QTableWidget.NoEditTriggers)
        table.setSelectionBehavior(QTableWidget.SelectRows)
        table.setSelectionMode(QTableWidget.MultiSelection)
        table.setContextMenuPolicy(Qt.ActionsContextMenu)
        self.add_actions(table, (self.edit_paste_action, self.edit_copy_action, self.edit_cut_action,
                                 self.edit_add_resource_action, self.edit_edit_resource_action,
                                 self.edit_remove_resource_action, self.edit_move_up_action,
                                 self.edit_move_down_action, self.edit_update_action))

        for row, resource in enumerate(resources):
            alias = QTableWidgetItem(resource.alias())
            file = QTableWidgetItem(resource.file())
            if resources.is_duplicate(resource.alias()):
                alias.setForeground(Qt.red)
            else:
                alias.setForeground(Qt.black)
            if os.path.isfile(os.path.join(os.path.dirname(self.collection.file_name()), resource.file())):
                file.setForeground(Qt.black)
            else:
                file.setForeground(Qt.red)
            table.setItem(row, 0, alias)
            table.setItem(row, 1, file)
        table.resizeColumnsToContents()

        for index in current_indexes:
            table.selectRow(index)

        table.setFocus()
        return table

    def update_ui(self):
        """Update the ui enabling and disabling actions.
        """

        file_name_exist = (file_name := self.collection.file_name()) is not None
        table_exist = (table := self.central_widget.currentWidget()) is not None
        resource_selected = table_exist and len(table.selectionModel().selectedRows()) > 0
        multiple_rows = table_exist and table.rowCount() > 1
        multiple_tables = len(self.collection) > 1

        self.setWindowTitle("QRC Editor - {0}[*]".format(os.path.basename(file_name)))
        self.setWindowModified(self.collection.dirty())

        if table_exist:
            self.edit_edit_tab_action.setEnabled(True)
            self.edit_remove_tab_action.setEnabled(True)
        else:
            self.edit_edit_tab_action.setEnabled(False)
            self.edit_remove_tab_action.setEnabled(False)

        if resource_selected:
            self.edit_edit_resource_action.setEnabled(True)
            self.edit_remove_resource_action.setEnabled(True)
            self.edit_copy_action.setEnabled(True)
            self.edit_cut_action.setEnabled(True)
        else:
            self.edit_edit_resource_action.setEnabled(False)
            self.edit_remove_resource_action.setEnabled(False)
            self.edit_copy_action.setEnabled(False)
            self.edit_cut_action.setEnabled(False)

        if file_name_exist and table_exist:
            self.edit_add_resource_action.setEnabled(True)
            self.file_compile_action.setEnabled(True)
        else:
            self.file_compile_action.setEnabled(False)
            self.edit_add_resource_action.setEnabled(False)

        if multiple_rows and resource_selected:
            indexes = [selected.row() for selected in table.selectionModel().selectedRows()]
            self.edit_move_down_action.setEnabled(max(indexes) < table.rowCount() - 1)
            self.edit_move_up_action.setEnabled(min(indexes) > 0)
        else:
            self.edit_move_down_action.setEnabled(False)
            self.edit_move_up_action.setEnabled(False)

        if multiple_tables:
            self.edit_move_left_action.setEnabled((index := self.central_widget.currentIndex()) > 0)
            self.edit_move_right_action.setEnabled(index < len(self.collection) - 1)
        else:
            self.edit_move_left_action.setEnabled(False)
            self.edit_move_right_action.setEnabled(False)

        self.edit_sort_action.setEnabled(multiple_rows)
        self.edit_update_action.setEnabled(len(self.collection) > 0)

    def update_widget(self, current=None):
        """Update the central widget populating the tabs.

        Parameters:
        current (int): the index of the current tab, to keep it in focus
        """

        self.central_widget.clear()
        for index, resources in enumerate(self.collection):
            title = ""
            if index < 10:
                title += "&{0} - Lang:  ".format(index)
            else:
                title += "{0} - Lang:  ".format(index)
            language = resources.language() if resources.language() is not None else "Default"
            title += language
            if resources.prefix() is not None:
                title += " - Prefix: {0}".format(resources.prefix())
            table = QTableWidget()
            self.update_table(table, resources)
            table.itemSelectionChanged.connect(self.update_ui)
            table.itemDoubleClicked.connect(self.edit_edit_resource)
            QShortcut(QKeySequence("Return"), table, self.edit_edit_resource)
            self.central_widget.addTab(table, QIcon(":/icon.png"), title)

        if current:
            self.central_widget.setCurrentIndex(current)

    def update_window_menu(self):
        """Update the window menu dynamically.
        """

        self.window_menu.clear()
        menu = self.window_menu
        if len(QrcEditor.instances) > 1:
            self.add_actions(menu, (self.window_arrange_horizontal_action, self.window_arrange_vertical_action, None))
        i = 1
        for editor in QrcEditor.instances:
            title = editor.windowTitle()[:-3]
            shortcut = ""
            if i == 10:
                menu.addSeparator()
                menu = menu.addMenu("&More")
            if i < 10:
                shortcut = "&{0} ".format(i)
            elif i < 36:
                shortcut = "&{0} ".format(chr(i + ord("@") - 9))
            action = menu.addAction("{0}{1}".format(shortcut, title))
            action.triggered.connect(self.raise_window)
            i += 1

    def window_arrange_horizontal(self):
        """Arrange the open windows horizontally.
        """

        size = self.screen().geometry()
        top = size.top()
        left = size.left()
        height = size.height() // len(QrcEditor.instances)
        width = size.width()
        for instance in QrcEditor.instances:
            instance.showNormal()
            instance.move(left, top)
            instance.resize(width, height)
            top += height

    def window_arrange_vertical(self):
        """Arrange the open windows vertically.
        """

        size = self.screen().geometry()
        top = size.top()
        left = size.left()
        height = size.height()
        width = size.width() // len(QrcEditor.instances)
        for instance in QrcEditor.instances:
            instance.showNormal()
            instance.move(left, top)
            instance.resize(width, height)
            left += width


if __name__ == "__main__":
    APP = QApplication(sys.argv)
    APP.setOrganizationName("Sanfe Ltd.")
    APP.setOrganizationDomain("sanfe.com")
    APP.setApplicationName("QRC Editor")
    APP.setWindowIcon(QIcon(":/icon.png"))
    if len(sys.argv) > 1 and str(sys.argv[1]) == "-reset":
        QSettings().clear()
    MAIN_WINDOW = QrcEditor()
    MAIN_WINDOW.show()
    APP.exec()
