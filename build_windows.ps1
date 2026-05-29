$ErrorActionPreference = "Stop"
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
pyinstaller --clean --onefile --windowed --name "Communication Database Converter" main.py
Write-Host "Executable created under dist\Communication Database Converter.exe"
