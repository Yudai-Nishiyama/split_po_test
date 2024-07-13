@echo off
setlocal

:: Pythonの環境を指定
set PYTHON_ENV=C:\Users\21332\anaconda3\envs\po_sprit\python.exe

:: スクリプトのパスを指定
set SCRIPT_PATH=%~dp0split_pdf.py

:: CSVファイルのパス
set CSV_PATH=%~dp0shizaihin.csv

:: 出力フォルダのパスを設定し、存在しない場合は作成
set OUTPUT_FOLDER=%~dp0output
if not exist "%OUTPUT_FOLDER%" mkdir "%OUTPUT_FOLDER%"

echo Looking for PDF files in %~dp0
:: 入力PDFファイルのパスを設定し、すべてのPDFファイルを対象にする
for %%F in (%~dp0*.pdf) do (
    echo Processing file: %%F
    :: スクリプトを実行
    "%PYTHON_ENV%" "%SCRIPT_PATH%" "%%F" "%CSV_PATH%" "%OUTPUT_FOLDER%"
)

if not exist %~dp0*.pdf echo No PDF files found in %~dp0

endlocal
pause