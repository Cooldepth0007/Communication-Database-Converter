from __future__ import annotations

from pathlib import Path


SUPPORTED_EXTENSIONS = {
    ".dbc": "DBC",
    ".arxml": "ARXML",
    ".xml": "XML",
    ".fibex": "FIBEX",
    ".ldf": "LDF",
}


class ValidationError(ValueError):
    """Raised when a selected input file cannot be processed."""


def detect_file_type(path: Path) -> str:
    suffix = path.suffix.lower()
    if suffix not in SUPPORTED_EXTENSIONS:
        raise ValidationError(f"Unsupported file extension: {suffix or '<none>'}")
    if suffix == ".xml":
        return _detect_xml_family(path)
    return SUPPORTED_EXTENSIONS[suffix]


def validate_input_file(path: Path) -> None:
    if not path.exists():
        raise ValidationError("File does not exist.")
    if not path.is_file():
        raise ValidationError("Path is not a file.")
    if path.stat().st_size == 0:
        raise ValidationError("File is empty.")
    detect_file_type(path)


def _detect_xml_family(path: Path) -> str:
    try:
        sample = path.read_bytes()[:8192].lower()
    except OSError:
        return "XML"
    if b"fibex" in sample or b":fibex" in sample:
        return "FIBEX"
    if b"autosar" in sample or b":autosar" in sample:
        return "ARXML"
    return "XML"
