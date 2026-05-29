from __future__ import annotations

from pathlib import Path

from lxml import etree

from communication_database_converter.models import ParsedDatabase
from communication_database_converter.parsers.common_xml import first_text, iter_by_local_name, parse_xml


class FibexParser:
    def parse(self, path: Path) -> ParsedDatabase:
        parsed = ParsedDatabase(source_file=path, file_type="FIBEX")
        try:
            root = parse_xml(path).getroot()
            clusters = list(iter_by_local_name(root, "CLUSTER"))
            frames = list(iter_by_local_name(root, "FRAME"))
            signals = list(iter_by_local_name(root, "SIGNAL"))
            parsed.add_row(
                "Network Summary",
                {
                    "Source File": path.name,
                    "File Type": "FIBEX",
                    "Cluster": ", ".join(filter(None, [first_text(item, ["SHORT-NAME", "NAME"]) for item in clusters[:5]])),
                    "Frames": len(frames),
                    "Signals": len(signals),
                },
            )
            for frame in frames:
                parsed.add_row(
                    "Messages",
                    {
                        "Source File": path.name,
                        "Cluster": "",
                        "Channel": first_text(frame, ["CHANNEL", "CHANNEL-REF"]),
                        "Frame": first_text(frame, ["SHORT-NAME", "NAME"]),
                        "Slot ID": first_text(frame, ["SLOT-ID", "SLOT"]),
                        "Cycle": first_text(frame, ["CYCLE", "BASE-CYCLE"]),
                        "Length": first_text(frame, ["BYTE-LENGTH", "LENGTH"]),
                        "Sender": first_text(frame, ["TRANSMITTER", "SENDER", "ECU-REF"]),
                        "Receiver": first_text(frame, ["RECEIVER", "ECU-REF"]),
                    },
                )
            for signal in signals:
                parsed.add_row(
                    "Signals",
                    {
                        "Source File": path.name,
                        "Signal": first_text(signal, ["SHORT-NAME", "NAME"]),
                        "Length": first_text(signal, ["BIT-LENGTH", "LENGTH"]),
                        "Offset": first_text(signal, ["BIT-POSITION", "OFFSET", "POSITION"]),
                        "Sender": first_text(signal, ["TRANSMITTER", "SENDER", "ECU-REF"]),
                        "Receiver": first_text(signal, ["RECEIVER", "ECU-REF"]),
                    },
                )
        except etree.XMLSyntaxError as exc:
            parsed.add_error(f"Invalid FIBEX XML: {exc}")
        except Exception as exc:
            parsed.add_error(f"FIBEX parse failed: {exc}")
        return parsed.finalize()
