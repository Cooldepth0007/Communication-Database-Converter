from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Callable

from communication_database_converter.exporters.csv_exporter import export_csv
from communication_database_converter.exporters.excel_exporter import export_excel
from communication_database_converter.models import ParsedDatabase, merge_databases
from communication_database_converter.parsers import parse_database
from communication_database_converter.utils.validators import validate_input_file


ProgressCallback = Callable[[int, str], None]


@dataclass(slots=True)
class ConversionOptions:
    input_files: list[Path]
    output_format: str
    output_path: Path
    single_output: bool = True


@dataclass(slots=True)
class ConversionResult:
    outputs: list[Path]
    parsed: list[ParsedDatabase]


def convert(options: ConversionOptions, progress: ProgressCallback | None = None) -> ConversionResult:
    parsed_databases: list[ParsedDatabase] = []
    total = max(len(options.input_files), 1)

    for index, input_file in enumerate(options.input_files, start=1):
        _progress(progress, int((index - 1) / total * 70), f"Validating {input_file.name}")
        validate_input_file(input_file)
        _progress(progress, int((index - 0.5) / total * 70), f"Parsing {input_file.name}")
        parsed_databases.append(parse_database(input_file))

    _progress(progress, 80, "Exporting data")
    outputs: list[Path] = []
    if options.single_output:
        merged = merge_databases(parsed_databases)
        if options.output_format == "Excel":
            outputs.append(export_excel(merged, options.output_path))
        else:
            csv_dir = options.output_path.parent if options.output_path.suffix else options.output_path
            outputs.extend(export_csv(merged, csv_dir))
    else:
        for parsed in parsed_databases:
            if options.output_format == "Excel":
                outputs.append(export_excel(parsed.sections, options.output_path / f"{parsed.source_file.stem}.xlsx"))
            else:
                outputs.extend(export_csv(parsed.sections, options.output_path / parsed.source_file.stem))
    _progress(progress, 100, "Conversion complete")
    return ConversionResult(outputs=outputs, parsed=parsed_databases)


def _progress(callback: ProgressCallback | None, percent: int, message: str) -> None:
    if callback:
        callback(max(0, min(percent, 100)), message)
