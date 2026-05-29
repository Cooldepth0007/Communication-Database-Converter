from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


SectionRows = dict[str, list[dict[str, Any]]]


SECTION_ORDER = [
    "Network Summary",
    "Messages",
    "Signals",
    "Nodes",
    "Diagnostics",
    "Errors and Warnings",
]


@dataclass(slots=True)
class ParsedDatabase:
    source_file: Path
    file_type: str
    sections: SectionRows = field(default_factory=dict)
    warnings: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)

    def add_row(self, section: str, row: dict[str, Any]) -> None:
        self.sections.setdefault(section, []).append(row)

    def add_warning(self, message: str) -> None:
        self.warnings.append(message)

    def add_error(self, message: str) -> None:
        self.errors.append(message)

    def finalize(self) -> "ParsedDatabase":
        issue_rows = []
        for warning in self.warnings:
            issue_rows.append(
                {"Source File": self.source_file.name, "Severity": "Warning", "Message": warning}
            )
        for error in self.errors:
            issue_rows.append(
                {"Source File": self.source_file.name, "Severity": "Error", "Message": error}
            )
        if issue_rows:
            self.sections.setdefault("Errors and Warnings", []).extend(issue_rows)
        for section in SECTION_ORDER:
            self.sections.setdefault(section, [])
        return self


def merge_databases(databases: list[ParsedDatabase]) -> SectionRows:
    merged: SectionRows = {section: [] for section in SECTION_ORDER}
    for database in databases:
        for section in SECTION_ORDER:
            merged.setdefault(section, []).extend(database.sections.get(section, []))
    return merged
