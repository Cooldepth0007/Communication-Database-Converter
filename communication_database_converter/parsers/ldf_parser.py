from __future__ import annotations

import re
from pathlib import Path

from communication_database_converter.models import ParsedDatabase


class LdfParser:
    def parse(self, path: Path) -> ParsedDatabase:
        parsed = ParsedDatabase(source_file=path, file_type="LDF")
        try:
            text = path.read_text(encoding="utf-8", errors="replace")
            cluster = _match(r"LIN_protocol_version\s*=\s*\"?([^\";]+)", text) or path.stem
            nodes = self._parse_nodes(text)
            frames = self._parse_frames(text)
            signals = self._parse_signals(text)
            schedules = self._parse_schedules(text)
            parsed.add_row(
                "Network Summary",
                {
                    "Source File": path.name,
                    "File Type": "LDF",
                    "LIN Cluster": cluster,
                    "Frames": len(frames),
                    "Signals": len(signals),
                    "Nodes": len(nodes),
                    "Schedule Tables": len(schedules),
                },
            )
            for node in nodes:
                parsed.add_row("Nodes", {"Source File": path.name, "Node Name": node})
            for frame in frames:
                parsed.add_row("Messages", {"Source File": path.name, "LIN Cluster": cluster, **frame})
            for signal in signals:
                parsed.add_row("Signals", {"Source File": path.name, **signal})
            for schedule in schedules:
                parsed.add_row("Diagnostics", {"Source File": path.name, "Schedule Table Information": schedule})
        except Exception as exc:
            parsed.add_error(f"LDF parse failed: {exc}")
        return parsed.finalize()

    @staticmethod
    def _parse_nodes(text: str) -> list[str]:
        block = _block("Nodes", text)
        return re.findall(r"\b[A-Za-z_][\w]*\b", block)

    @staticmethod
    def _parse_frames(text: str) -> list[dict[str, str]]:
        block = _block("Frames", text)
        rows = []
        for match in re.finditer(r"(\w+)\s*:\s*([0-9A-Fa-fx]+)\s*,\s*(\w+)\s*,\s*(\d+)\s*\{([^}]*)\}", block, re.S):
            subscribers = ", ".join(re.findall(r"\b[A-Za-z_]\w*\b", match.group(5)))
            rows.append(
                {
                    "Frame Name": match.group(1),
                    "Frame ID": match.group(2),
                    "Publisher": match.group(3),
                    "Subscriber": subscribers,
                    "Length": match.group(4),
                }
            )
        return rows

    @staticmethod
    def _parse_signals(text: str) -> list[dict[str, str]]:
        block = _block("Signals", text)
        rows = []
        for match in re.finditer(r"(\w+)\s*:\s*(\d+)\s*,\s*([^,;]+)", block):
            rows.append(
                {
                    "Signal Name": match.group(1),
                    "Signal Length": match.group(2),
                    "Initial Value": match.group(3).strip(),
                }
            )
        return rows

    @staticmethod
    def _parse_schedules(text: str) -> list[str]:
        block = _block("Schedule_tables", text)
        return [line.strip() for line in block.splitlines() if line.strip()]


def _block(name: str, text: str) -> str:
    match = re.search(rf"{name}\s*\{{(.*?)\n\}}", text, re.S)
    return match.group(1) if match else ""


def _match(pattern: str, text: str) -> str:
    match = re.search(pattern, text)
    return match.group(1).strip() if match else ""
