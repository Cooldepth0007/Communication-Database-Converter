from __future__ import annotations

import traceback

from PySide6.QtCore import QObject, QRunnable, Signal, Slot

from communication_database_converter.converter import ConversionOptions, convert


class WorkerSignals(QObject):
    progress = Signal(int, str)
    log = Signal(str)
    finished = Signal(object)
    failed = Signal(str)


class ConversionWorker(QRunnable):
    def __init__(self, options: ConversionOptions) -> None:
        super().__init__()
        self.options = options
        self.signals = WorkerSignals()

    @Slot()
    def run(self) -> None:
        try:
            result = convert(self.options, self.signals.progress.emit)
            self.signals.finished.emit(result)
        except Exception as exc:
            self.signals.failed.emit(f"{exc}\n\n{traceback.format_exc()}")
