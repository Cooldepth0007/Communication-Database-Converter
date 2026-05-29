from __future__ import annotations

import logging
from pathlib import Path

from PySide6.QtCore import QSettings, Qt, QThreadPool
from PySide6.QtGui import QAction
from PySide6.QtWidgets import (
    QApplication,
    QCheckBox,
    QComboBox,
    QFileDialog,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QMainWindow,
    QMessageBox,
    QPlainTextEdit,
    QProgressBar,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)

from communication_database_converter.converter import ConversionOptions, ConversionResult
from communication_database_converter.ui.workers import ConversionWorker
from communication_database_converter.utils.logger import configure_logging
from communication_database_converter.utils.validators import SUPPORTED_EXTENSIONS, ValidationError, validate_input_file


class DropListWidget(QListWidget):
    def __init__(self) -> None:
        super().__init__()
        self.setAcceptDrops(True)
        self.setSelectionMode(QListWidget.ExtendedSelection)

    def dragEnterEvent(self, event) -> None:  # noqa: N802
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dragMoveEvent(self, event) -> None:  # noqa: N802
        event.acceptProposedAction()

    def dropEvent(self, event) -> None:  # noqa: N802
        for url in event.mimeData().urls():
            path = Path(url.toLocalFile())
            if path.suffix.lower() in SUPPORTED_EXTENSIONS:
                self.addItem(str(path))


class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("Communication Database Converter")
        self.resize(1120, 760)
        self.settings = QSettings("Codex", "CommunicationDatabaseConverter")
        self.thread_pool = QThreadPool.globalInstance()
        self.logger = configure_logging()
        self._build_ui()
        self._load_settings()

    def _build_ui(self) -> None:
        central = QWidget()
        root = QVBoxLayout(central)

        self.input_list = DropListWidget()
        self.input_list.setToolTip("Drag and drop .dbc, .arxml, .xml, .fibex, or .ldf files here.")

        toolbar = QHBoxLayout()
        add_button = QPushButton("Select Input File(s)")
        add_button.clicked.connect(self.add_files)
        remove_button = QPushButton("Remove Selected")
        remove_button.clicked.connect(self.remove_selected)
        clear_button = QPushButton("Clear")
        clear_button.clicked.connect(self.input_list.clear)
        toolbar.addWidget(add_button)
        toolbar.addWidget(remove_button)
        toolbar.addWidget(clear_button)
        toolbar.addStretch()
        root.addLayout(toolbar)

        root.addWidget(self.input_list, 2)

        options = QHBoxLayout()
        self.format_combo = QComboBox()
        self.format_combo.addItems(["Excel", "CSV"])
        self.single_output = QCheckBox("Single output")
        self.single_output.setChecked(True)
        self.dark_mode = QCheckBox("Dark mode")
        self.dark_mode.toggled.connect(self.apply_theme)
        options.addWidget(QLabel("Output format"))
        options.addWidget(self.format_combo)
        options.addWidget(self.single_output)
        options.addWidget(self.dark_mode)
        options.addStretch()
        root.addLayout(options)

        output = QHBoxLayout()
        self.output_path = QLineEdit()
        browse_output = QPushButton("Browse")
        browse_output.clicked.connect(self.choose_output)
        output.addWidget(QLabel("Output"))
        output.addWidget(self.output_path, 1)
        output.addWidget(browse_output)
        root.addLayout(output)

        controls = QHBoxLayout()
        self.convert_button = QPushButton("Convert")
        self.convert_button.clicked.connect(self.start_conversion)
        self.progress = QProgressBar()
        self.status = QLabel("Ready")
        controls.addWidget(self.convert_button)
        controls.addWidget(self.progress, 1)
        controls.addWidget(self.status)
        root.addLayout(controls)

        tabs = QTabWidget()
        self.preview = QTableWidget()
        self.preview.setSortingEnabled(True)
        self.search = QLineEdit()
        self.search.setPlaceholderText("Search preview")
        self.search.textChanged.connect(self.filter_preview)
        preview_page = QWidget()
        preview_layout = QVBoxLayout(preview_page)
        preview_layout.addWidget(self.search)
        preview_layout.addWidget(self.preview)
        tabs.addTab(preview_page, "Preview")
        self.log = QPlainTextEdit()
        self.log.setReadOnly(True)
        tabs.addTab(self.log, "Conversion Log")
        root.addWidget(tabs, 3)

        self.setCentralWidget(central)
        self._create_menu()

    def _create_menu(self) -> None:
        file_menu = self.menuBar().addMenu("File")
        add_action = QAction("Add files", self)
        add_action.triggered.connect(self.add_files)
        file_menu.addAction(add_action)
        exit_action = QAction("Exit", self)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

    def _load_settings(self) -> None:
        self.output_path.setText(self.settings.value("last_output", str(Path.cwd() / "Converted_Output.xlsx")))
        self.dark_mode.setChecked(self.settings.value("dark_mode", False, type=bool))

    def add_files(self) -> None:
        files, _ = QFileDialog.getOpenFileNames(
            self,
            "Select communication database files",
            "",
            "Communication files (*.dbc *.arxml *.xml *.fibex *.ldf);;All files (*.*)",
        )
        for file_name in files:
            self.input_list.addItem(file_name)

    def remove_selected(self) -> None:
        for item in self.input_list.selectedItems():
            self.input_list.takeItem(self.input_list.row(item))

    def choose_output(self) -> None:
        if self.format_combo.currentText() == "Excel" and self.single_output.isChecked():
            file_name, _ = QFileDialog.getSaveFileName(self, "Save Excel file", self.output_path.text(), "Excel (*.xlsx)")
            if file_name:
                self.output_path.setText(file_name)
        else:
            folder = QFileDialog.getExistingDirectory(self, "Select output folder", self.output_path.text())
            if folder:
                self.output_path.setText(folder)

    def start_conversion(self) -> None:
        input_files = [Path(self.input_list.item(index).text()) for index in range(self.input_list.count())]
        if not input_files:
            QMessageBox.warning(self, "No input files", "Select at least one input file.")
            return
        try:
            for input_file in input_files:
                validate_input_file(input_file)
        except ValidationError as exc:
            QMessageBox.critical(self, "Validation failed", str(exc))
            return

        output = Path(self.output_path.text()).expanduser()
        if not output:
            QMessageBox.warning(self, "No output", "Select an output file or folder.")
            return
        self.settings.setValue("last_output", str(output))
        self.settings.setValue("dark_mode", self.dark_mode.isChecked())
        self.logger = configure_logging(output if output.suffix == "" else output.parent)
        self.convert_button.setEnabled(False)
        self.progress.setValue(0)
        self.log_message("Starting conversion")
        options = ConversionOptions(input_files, self.format_combo.currentText(), output, self.single_output.isChecked())
        worker = ConversionWorker(options)
        worker.signals.progress.connect(self.on_progress)
        worker.signals.finished.connect(self.on_finished)
        worker.signals.failed.connect(self.on_failed)
        self.thread_pool.start(worker)

    def on_progress(self, percent: int, message: str) -> None:
        self.progress.setValue(percent)
        self.status.setText(message)
        self.log_message(message)

    def on_finished(self, result: ConversionResult) -> None:
        self.convert_button.setEnabled(True)
        self.status.setText("Done")
        for output in result.outputs:
            self.log_message(f"Wrote {output}")
        self.populate_preview(result)
        self.logger.info("Conversion result: success; outputs=%s", ", ".join(str(item) for item in result.outputs))
        QMessageBox.information(self, "Conversion complete", f"Created {len(result.outputs)} output file(s).")

    def on_failed(self, message: str) -> None:
        self.convert_button.setEnabled(True)
        self.status.setText("Failed")
        self.log_message(message)
        self.logger.error(message)
        QMessageBox.critical(self, "Conversion failed", message.splitlines()[0])

    def populate_preview(self, result: ConversionResult) -> None:
        rows = []
        for database in result.parsed:
            rows.extend(database.sections.get("Signals", [])[:500])
        self.preview.setRowCount(len(rows))
        columns = sorted({key for row in rows for key in row.keys()})
        self.preview.setColumnCount(len(columns))
        self.preview.setHorizontalHeaderLabels(columns)
        for row_index, row in enumerate(rows):
            for column_index, column in enumerate(columns):
                self.preview.setItem(row_index, column_index, QTableWidgetItem(str(row.get(column, ""))))
        self.preview.resizeColumnsToContents()

    def filter_preview(self, text: str) -> None:
        needle = text.lower()
        for row in range(self.preview.rowCount()):
            visible = not needle
            if needle:
                for column in range(self.preview.columnCount()):
                    item = self.preview.item(row, column)
                    if item and needle in item.text().lower():
                        visible = True
                        break
            self.preview.setRowHidden(row, not visible)

    def log_message(self, message: str) -> None:
        self.log.appendPlainText(message)
        self.logger.info(message)

    def apply_theme(self, enabled: bool) -> None:
        app = QApplication.instance()
        if not app:
            return
        if enabled:
            app.setStyleSheet(
                """
                QWidget { background: #20242a; color: #f1f3f5; }
                QLineEdit, QPlainTextEdit, QListWidget, QTableWidget, QComboBox {
                    background: #111418; border: 1px solid #4a5563; padding: 4px;
                }
                QPushButton { background: #2f6fed; color: white; border: 0; padding: 7px 12px; }
                QPushButton:disabled { background: #555b64; }
                """
            )
        else:
            app.setStyleSheet("")

    def closeEvent(self, event) -> None:  # noqa: N802
        self.settings.setValue("last_output", self.output_path.text())
        self.settings.setValue("dark_mode", self.dark_mode.isChecked())
        super().closeEvent(event)
