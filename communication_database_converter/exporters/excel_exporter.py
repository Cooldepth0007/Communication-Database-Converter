from __future__ import annotations

from pathlib import Path

import pandas as pd

from communication_database_converter.models import SECTION_ORDER, SectionRows


def export_excel(sections: SectionRows, output_file: Path) -> Path:
    output_file.parent.mkdir(parents=True, exist_ok=True)
    if output_file.suffix.lower() != ".xlsx":
        output_file = output_file.with_suffix(".xlsx")
    with pd.ExcelWriter(output_file, engine="openpyxl") as writer:
        for section in SECTION_ORDER:
            rows = sections.get(section, [])
            sheet_name = _sheet_name(section)
            frame = pd.DataFrame(rows)
            if frame.empty:
                frame = pd.DataFrame([{"Status": "No data extracted"}])
            frame.to_excel(writer, sheet_name=sheet_name, index=False)
            worksheet = writer.sheets[sheet_name]
            for column_cells in worksheet.columns:
                max_length = max(len(str(cell.value or "")) for cell in column_cells)
                worksheet.column_dimensions[column_cells[0].column_letter].width = min(max(max_length + 2, 12), 70)
    return output_file


def _sheet_name(section: str) -> str:
    mapping = {
        "Network Summary": "Network Summary",
        "Messages": "Messages Frames",
        "Signals": "Signals",
        "Nodes": "ECUs Nodes",
        "Diagnostics": "Diagnostics",
        "Errors and Warnings": "Errors Warnings",
    }
    return mapping.get(section, section)[:31]
