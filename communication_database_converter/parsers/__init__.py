from __future__ import annotations

from pathlib import Path

from communication_database_converter.models import ParsedDatabase
from communication_database_converter.parsers.arxml_parser import ArxmlParser
from communication_database_converter.parsers.dbc_parser import DbcParser
from communication_database_converter.parsers.fibex_parser import FibexParser
from communication_database_converter.parsers.ldf_parser import LdfParser
from communication_database_converter.utils.validators import detect_file_type


def parse_database(path: Path) -> ParsedDatabase:
    file_type = detect_file_type(path)
    if file_type == "DBC":
        return DbcParser().parse(path)
    if file_type == "LDF":
        return LdfParser().parse(path)
    if file_type == "FIBEX":
        return FibexParser().parse(path)
    return ArxmlParser(xml_mode=file_type == "XML").parse(path)
