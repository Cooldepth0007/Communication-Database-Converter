from __future__ import annotations

import re
from pathlib import Path

from lxml import etree

from communication_database_converter.models import ParsedDatabase
from communication_database_converter.parsers.common_xml import first_text, iter_by_local_name, local_name, parse_xml, text_of


class ArxmlParser:
    def __init__(self, xml_mode: bool = False) -> None:
        self.xml_mode = xml_mode

    def parse(self, path: Path) -> ParsedDatabase:
        parsed = ParsedDatabase(source_file=path, file_type="XML" if self.xml_mode else "ARXML")
        try:
            tree = parse_xml(path)
            root = tree.getroot()
            version = self._autosar_version(root)
            clusters = list(iter_by_local_name(root, "CAN-CLUSTER", "FLEXRAY-CLUSTER", "LIN-CLUSTER", "ETHERNET-CLUSTER"))
            frames = list(iter_by_local_name(root, "CAN-FRAME", "FLEXRAY-FRAME", "LIN-FRAME", "FRAME"))
            signals = list(iter_by_local_name(root, "I-SIGNAL", "SYSTEM-SIGNAL", "SIGNAL"))
            ecus = list(iter_by_local_name(root, "ECU-INSTANCE", "ECU-EXTRACT", "APPLICATION-SW-COMPONENT-TYPE"))
            parsed.add_row(
                "Network Summary",
                {
                    "Source File": path.name,
                    "File Type": parsed.file_type,
                    "AUTOSAR Version": version,
                    "Cluster Name": ", ".join(filter(None, [first_text(item, ["SHORT-NAME"]) for item in clusters[:5]])),
                    "Frames": len(frames),
                    "Signals": len(signals),
                    "Nodes": len(ecus),
                },
            )
            if not version and not self.xml_mode:
                parsed.add_warning("AUTOSAR version was not detected.")
            for cluster in clusters:
                parsed.add_row("Nodes", {"Source File": path.name, "Cluster Name": first_text(cluster, ["SHORT-NAME"]), "Node Name": ""})
            for ecu in ecus:
                parsed.add_row("Nodes", {"Source File": path.name, "Node Name": first_text(ecu, ["SHORT-NAME"]), "Cluster Name": ""})
            for frame in frames:
                parsed.add_row("Messages", self._frame_row(path.name, frame))
            for signal in signals:
                parsed.add_row("Signals", self._signal_row(path.name, signal))
            self._extract_diagnostics(path.name, parsed, root)
        except etree.XMLSyntaxError as exc:
            parsed.add_error(f"Invalid XML: {exc}")
        except Exception as exc:
            parsed.add_error(f"ARXML/XML parse failed: {exc}")
        return parsed.finalize()

    @staticmethod
    def _autosar_version(root: etree._Element) -> str:
        namespace_text = " ".join(root.nsmap.values()) if root.nsmap else ""
        match = re.search(r"AUTOSAR_(\d+-\d+-\d+)|autosar/(?:schema/)?r?(\d+\.\d+\.\d+)", namespace_text, re.I)
        if match:
            return next(group for group in match.groups() if group)
        return root.get("VERSION", "")

    @staticmethod
    def _frame_row(source_file: str, frame: etree._Element) -> dict[str, str]:
        return {
            "Source File": source_file,
            "Cluster Name": "",
            "Frame Name": first_text(frame, ["SHORT-NAME", "NAME"]),
            "Frame ID": first_text(frame, ["IDENTIFIER", "FRAME-ID"]),
            "PDU Name": first_text(frame, ["PDU-REF", "I-PDU-REF", "PDU-TRIGGERING-REF"]),
            "Length": first_text(frame, ["FRAME-LENGTH", "LENGTH"]),
            "Sender": first_text(frame, ["SENDER", "TRANSMITTER", "ECU-INSTANCE-REF"]),
            "Receiver": first_text(frame, ["RECEIVER", "RECEIVERS", "ECU-INSTANCE-REF"]),
        }

    @staticmethod
    def _signal_row(source_file: str, signal: etree._Element) -> dict[str, str]:
        return {
            "Source File": source_file,
            "Signal Name": first_text(signal, ["SHORT-NAME", "NAME"]),
            "Data Type": first_text(signal, ["BASE-TYPE-REF", "IMPLEMENTATION-DATA-TYPE-REF", "DATA-TYPE-REF"]),
            "Length": first_text(signal, ["LENGTH", "BIT-LENGTH"]),
            "Sender": first_text(signal, ["SENDER", "TRANSMITTER", "ECU-INSTANCE-REF"]),
            "Receiver": first_text(signal, ["RECEIVER", "RECEIVERS", "ECU-INSTANCE-REF"]),
            "Compu Method": first_text(signal, ["COMPU-METHOD-REF", "COMPU-METHOD"]),
            "Scaling": first_text(signal, ["COMPU-NUMERATOR", "SCALE", "FACTOR"]),
            "Offset": first_text(signal, ["COMPU-OFFSET", "OFFSET"]),
            "Unit": first_text(signal, ["UNIT-REF", "DISPLAY-NAME"]),
            "Initial Value": first_text(signal, ["INIT-VALUE", "INITIAL-VALUE", "VALUE"]),
            "Update Bit": first_text(signal, ["UPDATE-BIT-POSITION", "UPDATE-BIT"]),
            "Timeout Information": first_text(signal, ["TIMEOUT", "TIMEOUT-VALUE", "ALIVE-TIMEOUT"]),
        }

    @staticmethod
    def _extract_diagnostics(source_file: str, parsed: ParsedDatabase, root: etree._Element) -> None:
        for element in root.iter():
            name = local_name(element.tag)
            if "DIAG" in name.upper() or "DTC" in name.upper():
                value = text_of(element) or first_text(element, ["SHORT-NAME", "ID", "VALUE"])
                if value:
                    parsed.add_row("Diagnostics", {"Source File": source_file, "Type": name, "Value": value})
