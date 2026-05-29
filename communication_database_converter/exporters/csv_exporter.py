from __future__ import annotations

from pathlib import Path

import pandas as pd

from communication_database_converter.models import SECTION_ORDER, SectionRows


CSV_NAMES = {
    "Network Summary": "Network_Summary.csv",
    "Messages": "Messages.csv",
    "Signals": "Signals.csv",
    "Nodes": "Nodes.csv",
    "Diagnostics": "Diagnostics.csv",
    "Errors and Warnings": "Errors_and_Warnings.csv",
}


def export_csv(sections: SectionRows, output_dir: Path) -> list[Path]:
    output_dir.mkdir(parents=True, exist_ok=True)
    written = []
    for section in SECTION_ORDER:
        frame = pd.DataFrame(sections.get(section, []))
        if frame.empty:
            frame = pd.DataFrame([{"Status": "No data extracted"}])
        path = output_dir / CSV_NAMES[section]
        frame.to_csv(path, index=False, encoding="utf-8-sig")
        written.append(path)
    return written
