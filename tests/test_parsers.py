from pathlib import Path

from communication_database_converter.parsers import parse_database


ROOT = Path(__file__).resolve().parents[1]


def test_dbc_parser_extracts_message_and_signal():
    parsed = parse_database(ROOT / "sample_data" / "sample.dbc")
    assert parsed.sections["Messages"]
    assert any(row.get("Signal Name") == "EngineSpeed" for row in parsed.sections["Signals"])


def test_arxml_parser_extracts_signal():
    parsed = parse_database(ROOT / "sample_data" / "sample.arxml")
    assert parsed.sections["Network Summary"][0]["File Type"] == "ARXML"
    assert any(row.get("Signal Name") == "VehicleSpeed" for row in parsed.sections["Signals"])


def test_fibex_parser_extracts_frame():
    parsed = parse_database(ROOT / "sample_data" / "sample.fibex")
    assert any(row.get("Frame") == "FR_Static_Frame" for row in parsed.sections["Messages"])


def test_ldf_parser_extracts_frame():
    parsed = parse_database(ROOT / "sample_data" / "sample.ldf")
    assert any(row.get("Frame Name") == "DoorStatus" for row in parsed.sections["Messages"])
