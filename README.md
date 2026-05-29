# Communication Database Converter

Standalone Windows desktop application for converting automotive communication databases into Excel or CSV.

Supported inputs:

- DBC for CAN and CAN FD
- AUTOSAR ARXML
- Generic XML communication descriptions
- FlexRay FIBEX
- LIN LDF

## Features

- PySide6 desktop UI with drag-and-drop batch input
- Excel export with separate worksheets for network summary, messages/frames, signals, ECUs/nodes, diagnostics, and errors/warnings
- CSV export with one file per section
- Worker-thread conversion so the UI remains responsive
- Defensive validation and error logging to `Converter_Log.txt`
- Preview table with search/filter
- Remembered last output location
- Light and dark modes

## Project Layout

```text
communication_database_converter/
  ui/
  parsers/
  exporters/
  utils/
main.py
requirements.txt
build_windows.ps1
communication_database_converter.spec
tests/
sample_data/
```

## Development

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python main.py
```

## Build Portable EXE

```powershell
.\build_windows.ps1
```

Or directly:

```powershell
pyinstaller --onefile --windowed --name "Communication Database Converter" main.py
```

The executable is written to `dist\Communication Database Converter.exe` and can run on Windows 10/11 without a Python installation.

## Notes for Industrial Use

DBC parsing uses `cantools` for high-fidelity extraction. ARXML, XML, and FIBEX are namespace-tolerant and intentionally defensive because OEM/vendor schemas vary heavily. For unsupported or incomplete schema details, the converter records warnings instead of crashing. Very large files should be processed from local disk for best performance.
