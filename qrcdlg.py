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

from PySide2.QtCore import QLocale, Qt
from PySide2.QtGui import QIcon
from PySide2.QtWidgets import QAction, QCheckBox, QComboBox, QDialog, QDialogButtonBox, QFileDialog, QGridLayout,\
    QLabel, QLineEdit, QMessageBox, QSlider

import qrcdata


def languages_with_code():
    """Return a list of tuple with language name and language code.

    Return:
    list: list of tuple with language name and language code
    """

    languages = set()
    all_locales = QLocale.matchingLocales(QLocale.AnyLanguage, QLocale.AnyScript,
                                          QLocale.AnyCountry)
    for locale in all_locales:
        language = QLocale.languageToString(locale.language())
        code = locale.name().split("_")[0]
        languages.add("{0}_{1}".format(language, code))
    languages = sorted(language.split("_") for language in languages)
    languages.insert(0, ["Default", None])
    return languages


LANGUAGES = languages_with_code()


class ResourceDlg(QDialog):
    """Create a dialog to create/edit resource data.
    """

    def __init__(self, collection, resources_index, resource_index, resource_file=None, parent=None):
        """Constructor for the ResourceDlg class.
        """

        super(ResourceDlg, self).__init__(parent)

        self.collection = collection
        self.resources = self.collection[resources_index]
        if resource_file is not None:
            self.resource = None
            file_name = resource_file[1 + len(os.path.dirname(self.collection.file_name())):]
            alias = os.path.basename(resource_file)
            self.index = resource_index + 1
            title = "QRC Editor - Add Resource"
        else:
            self.resource = self.resources[resource_index]
            file_name = self.resource.file()
            alias = self.resource.alias()
            title = "QRC Editor - Edit Resource"
        file_label = QLabel("&File:")
        action = QAction("Browse for Resource", self)
        action.setIcon(QIcon(":/file_open.png"))
        action.setToolTip("Browse for Resource")
        action.setStatusTip("Browse for Resource")
        action.triggered.connect(self.update_file)
        self.file_line_edit = QLineEdit()
        self.file_line_edit.addAction(action, QLineEdit.TrailingPosition)
        file_label.setBuddy(self.file_line_edit)
        self.file_line_edit.setText(file_name)
        alias_label = QLabel("&Alias:")
        self.alias_line_edit = QLineEdit()
        alias_label.setBuddy(self.alias_line_edit)
        self.alias_line_edit.setText(alias)
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)

        layout = QGridLayout()
        layout.addWidget(file_label, 0, 0)
        layout.addWidget(self.file_line_edit, 0, 1)
        layout.addWidget(alias_label, 0, 2)
        layout.addWidget(self.alias_line_edit, 0, 3)
        layout.addWidget(button_box, 1, 0, 1, 4)

        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)

        self.setLayout(layout)
        self.setWindowTitle(title)

    def accept(self):
        """Add/Update the resource.
        """

        file = self.file_line_edit.text()
        if not file:
            return
        alias = self.alias_line_edit.text()

        if self.resource is None:
            self.resource = qrcdata.Resource(file, alias)
            self.resources.insert(self.index, self.resource)
            self.collection.set_dirty(True)
        else:
            if alias != self.resource.alias():
                self.resource.set_alias(alias)
                self.collection.set_dirty(True)
            if file != self.resource.file():
                self.resource.set_file(file)
                self.collection.set_dirty(True)

        QDialog.accept(self)

    def update_file(self):
        """Open dialog to update the file of the resource.
        """

        file_dlg = ResourceFileDlg(self.collection.file_name(), self.file_line_edit.text())
        if file_dlg.exec_():
            file_name = os.path.abspath(file_dlg.selectedFiles()[0])
            if file_name.startswith(os.path.abspath(os.path.dirname(self.collection.file_name()))):
                self.file_line_edit.setText(file_name[1 + len(os.path.dirname(self.collection.file_name())):])
            else:
                QMessageBox.warning(self, "File Error", "Selected file is not in a subdirectory of {0}"
                                    .format(os.path.basename(self.collection.file_name())))


class ResourceFileDlg(QFileDialog):
    """Create a non traversal dialog to add a resource.
    """

    def __init__(self, qrc_file, resource_file="", parent=None):
        """Constructor for the ResourceFileDlg.

        Parameters:
        file_path (str): the path of the .qrc file
        """

        super(ResourceFileDlg, self).__init__(parent)

        self.setNameFilter("Binary resource (*.*)")
        self.setWindowTitle("QRC Editor - Resource")
        self.path = os.path.realpath(os.path.dirname(qrc_file))
        path = os.path.realpath(os.path.dirname(os.path.join(self.path, resource_file)))
        if (not path.startswith(self.path)) or (not os.path.isdir(path)):
            path = self.path
        self.setDirectory(path)
        self.setFileMode(QFileDialog.FileMode.ExistingFile)

        self.directoryEntered.connect(self.check_path)

    def check_path(self):
        """Check if the directory is a subdirectory of the .qrc file.
        """

        if not os.path.realpath(self.directory().absolutePath()).startswith(self.path):
            self.setDirectory(self.path)


class ResourceSettingsDlg(QDialog):
    """Create a dialog to create/edit resource data.
    """

    def __init__(self, options, parent=None):
        """Constructor for the MovieDlg class.
        """

        super(ResourceSettingsDlg, self).__init__(parent)

        self.options = options

        program_label = QLabel("&Program:")
        action = QAction("Browse for File", self)
        action.setIcon(QIcon(":/file_open.png"))
        action.setToolTip("Browse for File")
        action.setStatusTip("Browse for File")
        action.triggered.connect(self.update_program)
        self.program_line_edit = QLineEdit()
        self.program_line_edit.addAction(action, QLineEdit.TrailingPosition)
        self.program_line_edit.setText(self.options["program"])
        self.program_line_edit.setReadOnly(True)
        program_label.setBuddy(self.program_line_edit)
        self.no_compress_checkbox = QCheckBox("&No compression")
        self.no_compress_checkbox.setChecked(self.options["no_compress"])

        self.compress_checkbox = QCheckBox("C&ompress")
        self.compress_checkbox.setChecked(self.options["compress"])
        self.compress_slider = QSlider()
        self.compress_slider.setOrientation(Qt.Horizontal)
        self.compress_slider.setRange(1, 9)
        self.compress_slider.setValue(self.options["compress_level"])
        self.compress_slider.setEnabled(self.options["compress"])

        self.threshold_checkbox = QCheckBox("&Threshold")
        self.threshold_checkbox.setChecked(self.options["threshold"])
        self.threshold_slider = QSlider()
        self.threshold_slider.setOrientation(Qt.Horizontal)
        self.threshold_slider.setValue(self.options["threshold_level"])
        self.threshold_slider.setEnabled(self.options["threshold"])
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel | QDialogButtonBox.Reset
                                      | QDialogButtonBox.Help)

        layout = QGridLayout()
        layout.addWidget(program_label, 0, 0)
        layout.addWidget(self.program_line_edit, 0, 1, 1, 2)
        layout.addWidget(self.no_compress_checkbox, 1, 0)
        layout.addWidget(self.compress_checkbox, 2, 0)
        layout.addWidget(self.compress_slider, 2, 1)
        layout.addWidget(self.threshold_checkbox, 3, 0)
        layout.addWidget(self.threshold_slider, 3, 1)
        layout.addWidget(button_box, 4, 0, 1, 3)

        self.no_compress_checkbox.clicked.connect(self.no_compress_slot)
        self.compress_checkbox.clicked.connect(self.compress_slot)
        self.threshold_checkbox.clicked.connect(self.threshold_slot)
        button_box.button(QDialogButtonBox.Reset).clicked.connect(self.reset)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        button_box.helpRequested.connect(self.help_dialog)

        self.setLayout(layout)
        self.setWindowTitle("QRC Editor - Settings")

    def accept(self):
        """Update the options dictionary.
        """

        self.options["program"] = self.program_line_edit.text()
        self.options["no_compress"] = self.no_compress_checkbox.isChecked()
        self.options["compress"] = self.compress_checkbox.isChecked()
        self.options["compress_level"] = self.compress_slider.value()
        self.options["threshold"] = self.threshold_checkbox.isChecked()
        self.options["threshold_level"] = self.threshold_slider.value()
        QDialog.accept(self)

    def compress_slot(self):
        """Change checkboxes status.
        """

        if self.compress_checkbox.isChecked():
            self.no_compress_checkbox.setChecked(False)
            self.compress_slider.setEnabled(True)
        else:
            self.compress_slider.setEnabled(False)

    def help_dialog(self):
        """Open the help dialog.
        """

        QMessageBox.information(self, "Help Message", self.parent().help_message)

    def no_compress_slot(self):
        """Change checkboxes status.
        """

        if self.no_compress_checkbox.isChecked():
            self.compress_checkbox.setChecked(False)
            self.compress_slider.setEnabled(False)
            self.threshold_checkbox.setChecked(False)
            self.threshold_slider.setEnabled(False)

    def reset(self):
        """Reset the options.
        """

        self.options["program"] = "pyside2-rcc.exe"
        self.options["no_compress"] = False
        self.options["compress"] = False
        self.options["compress_level"] = 1
        self.options["threshold"] = False
        self.options["threshold_level"] = 70
        self.program_line_edit.setText(self.options["program"])
        self.no_compress_checkbox.setChecked(self.options["no_compress"])
        self.compress_checkbox.setChecked(self.options["compress"])
        self.compress_slider.setValue(self.options["compress_level"])
        self.compress_slider.setEnabled(self.options["compress"])
        self.threshold_checkbox.setChecked(self.options["threshold"])
        self.threshold_slider.setValue(self.options["threshold_level"])
        self.threshold_slider.setEnabled(self.options["threshold"])

    def threshold_slot(self):
        """Change checkboxes status.
        """

        if self.threshold_checkbox.isChecked():
            self.no_compress_checkbox.setChecked(False)
            self.threshold_slider.setEnabled(True)
        else:
            self.threshold_slider.setEnabled(False)

    def update_program(self):
        """Open dialog to update the compiler.
        """

        file_name, _ = QFileDialog.getOpenFileName(self, "QRC Editor - Choose Compiler", ".",
                                                   "Executables (*.exe);;All Files (*.*)")
        if file_name and self.parent().check_program(file_name):
            self.program_line_edit.setText(file_name)
        else:
            QMessageBox.critical(self, "Error", "Invalid Program")


class TabDlg(QDialog):
    """Create a dialog to create/edit resources tab.
    """

    def __init__(self, collection, resources=None, index=None, parent=None):
        """Constructor for the ResourceDlg class.
        """

        super(TabDlg, self).__init__(parent)

        self.collection = collection
        self.resources = resources
        if self.resources is not None:
            title = "QRC Editor - Edit Tab"
            resources_language = self.resources.language()
            prefix = self.resources.prefix()
            self.index = self.collection.index(self.resources)
        else:
            title = "QRC Editor - Add Tab"
            resources_language = None
            prefix = ""
            self.index = index + 1
        language_label = QLabel("&Language:")
        self.language_combo_box = QComboBox()
        language_label.setBuddy(self.language_combo_box)
        current = 0
        for row, language in enumerate(LANGUAGES):
            self.language_combo_box.insertItem(row, language[0])
            if resources_language == language[1]:
                current = row
        self.language_combo_box.setCurrentIndex(current)
        prefix_label = QLabel("&Prefix:")
        self.prefix_line_edit = QLineEdit()
        prefix_label.setBuddy(self.prefix_line_edit)
        self.prefix_line_edit.setText(prefix)
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)

        layout = QGridLayout()
        layout.addWidget(language_label, 0, 0)
        layout.addWidget(self.language_combo_box, 0, 1)
        layout.addWidget(prefix_label, 0, 2)
        layout.addWidget(self.prefix_line_edit, 0, 3)
        layout.addWidget(button_box, 1, 0, 1, 4)

        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)

        self.setLayout(layout)
        self.setWindowTitle(title)

    def accept(self):
        """Add/Update the resource tab.
        """

        language = LANGUAGES[self.language_combo_box.currentIndex()][1]
        prefix = self.prefix_line_edit.text() if self.prefix_line_edit.text() != "" else None
        resources = qrcdata.Resources(language, prefix)

        if resources in self.collection:
            index = self.collection.index(resources)
            if self.resources is not None:
                reply = QMessageBox.question(self, "QRC Editor - Merge Tabs", "Tab already present, merge the tabs?",
                                             QMessageBox.Yes | QMessageBox.No)
                if reply == QMessageBox.Yes:
                    self.collection.set_dirty(True)
                    self.collection[index].extend(self.collection[self.index])
                    del self.collection[self.index]

            self.index = index if index < self.index else index - 1
        else:
            self.collection.set_dirty(True)
            if self.resources is not None:
                if language != self.resources.language():
                    self.resources.set_language(language)
                if prefix != self.resources.prefix():
                    self.resources.set_prefix(prefix)
            else:
                self.collection.insert(self.index, resources)

        QDialog.accept(self)


class TabSortDlg(QDialog):
    """Create a dialog to sort a tab.
    """

    def __init__(self, parent=None):
        """Constructor for the TabSortDlg class.
        """

        super(TabSortDlg, self).__init__(parent)

        key_label = QLabel("&Key:")
        self.key_combo_box = QComboBox()
        key_label.setBuddy(self.key_combo_box)
        self.key_combo_box.addItems(["Alias", "File name"])
        self.reverse_checkbox = QCheckBox("&Reverse order")
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)

        layout = QGridLayout()
        layout.addWidget(key_label, 0, 0)
        layout.addWidget(self.key_combo_box, 0, 1)
        layout.addWidget(self.reverse_checkbox, 0, 2)
        layout.addWidget(button_box, 1, 0, 1, 3)

        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)

        self.setLayout(layout)
        self.setWindowTitle("QRC Editor - Sort")
