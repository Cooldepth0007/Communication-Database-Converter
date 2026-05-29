from __future__ import annotations

from pathlib import Path
from typing import Any

from communication_database_converter.models import ParsedDatabase


class DbcParser:
    def parse(self, path: Path) -> ParsedDatabase:
        parsed = ParsedDatabase(source_file=path, file_type="DBC")
        try:
            import cantools

            database = cantools.database.load_file(str(path), strict=False)
            buses = getattr(database, "buses", None) or []
            nodes = getattr(database, "nodes", None) or []
            network_name = buses[0].name if buses else path.stem
            parsed.add_row(
                "Network Summary",
                {
                    "Source File": path.name,
                    "File Type": "DBC",
                    "Network Name": network_name,
                    "Messages": len(database.messages),
                    "Signals": sum(len(message.signals) for message in database.messages),
                    "Nodes": len(nodes),
                },
            )
            for node in nodes:
                parsed.add_row("Nodes", {"Source File": path.name, "Node Name": node.name, "Comment": node.comment or ""})
            for message in database.messages:
                is_fd = bool(getattr(message, "is_fd", False))
                message_row = {
                    "Source File": path.name,
                    "Network Name": network_name,
                    "Message Name": message.name,
                    "Message ID Hex": f"0x{message.frame_id:X}",
                    "Message ID Decimal": message.frame_id,
                    "DLC": message.length,
                    "Cycle Time": getattr(message, "cycle_time", "") or "",
                    "Transmitter ECU": ", ".join(message.senders or []),
                    "CAN Type": "CAN FD" if is_fd else "CAN",
                    "Comment": message.comment or "",
                }
                parsed.add_row("Messages", message_row)
                for signal in message.signals:
                    parsed.add_row("Signals", self._signal_row(path.name, network_name, message, signal, is_fd))
        except Exception as exc:
            parsed.add_error(f"DBC parse failed with cantools: {exc}")
            self._fallback_parse(path, parsed)
        return parsed.finalize()

    @staticmethod
    def _signal_row(source_file: str, network_name: str, message: Any, signal: Any, is_fd: bool) -> dict[str, Any]:
        scale = getattr(signal.conversion, "scale", getattr(signal, "scale", ""))
        offset = getattr(signal.conversion, "offset", getattr(signal, "offset", ""))
        return {
            "Source File": source_file,
            "Network Name": network_name,
            "Message Name": message.name,
            "Message ID Hex": f"0x{message.frame_id:X}",
            "Message ID Decimal": message.frame_id,
            "DLC": message.length,
            "Cycle Time": getattr(message, "cycle_time", "") or "",
            "Transmitter ECU": ", ".join(message.senders or []),
            "Signal Name": signal.name,
            "Start Bit": signal.start,
            "Length": signal.length,
            "Byte Order": signal.byte_order,
            "Signed/Unsigned": "Signed" if signal.is_signed else "Unsigned",
            "Factor": scale,
            "Offset": offset,
            "Minimum": signal.minimum if signal.minimum is not None else "",
            "Maximum": signal.maximum if signal.maximum is not None else "",
            "Unit": signal.unit or "",
            "Receiver ECU": ", ".join(signal.receivers or []),
            "Multiplexing Information": _multiplexing(signal),
            "CAN Type": "CAN FD" if is_fd else "CAN",
            "Comment": signal.comment or "",
        }

    @staticmethod
    def _fallback_parse(path: Path, parsed: ParsedDatabase) -> None:
        parsed.add_warning("Using limited DBC text fallback; install cantools for full fidelity.")
        try:
            for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
                if line.startswith("BO_ "):
                    parts = line.split()
                    if len(parts) >= 5:
                        frame_id = int(parts[1])
                        parsed.add_row(
                            "Messages",
                            {
                                "Source File": path.name,
                                "Message Name": parts[2].rstrip(":"),
                                "Message ID Hex": f"0x{frame_id:X}",
                                "Message ID Decimal": frame_id,
                                "DLC": parts[3],
                                "Transmitter ECU": parts[4],
                            },
                        )
        except Exception as exc:
            parsed.add_error(f"DBC fallback parse failed: {exc}")


def _multiplexing(signal: Any) -> str:
    if getattr(signal, "is_multiplexer", False):
        return "Multiplexer"
    ids = getattr(signal, "multiplexer_ids", None)
    if ids:
        return "Mux " + ", ".join(str(item) for item in ids)
    return ""
