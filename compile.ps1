Param(
    [Parameter(Mandatory=$true)]
    [string]$FileToCompile
)

# Definiere Pfade
$MetaEditorPath = "C:\Program Files\MetaTrader 5\metaeditor64.exe"
$LogFile = $FileToCompile + ".log"
$IncludePath = "C:\Users\$env:USERNAME\AppData\Roaming\MetaQuotes\Terminal\D0E8209F77C8CF37AD8BF550E51FF075\MQL5"
$CompileBat = Join-Path $PSScriptRoot "compile.bat"

Write-Host "=== MetaEditor Kompilierung ===" -ForegroundColor Cyan
Write-Host "Datei: $FileToCompile" -ForegroundColor Yellow
Write-Host "Log: $LogFile" -ForegroundColor Yellow
Write-Host "Include: $IncludePath" -ForegroundColor Yellow

# Prüfe ob MetaEditor existiert
if (-not (Test-Path $MetaEditorPath)) {
    Write-Host "FEHLER: MetaEditor nicht gefunden: $MetaEditorPath" -ForegroundColor Red
    exit 1
}

# Prüfe ob Source-Datei existiert
if (-not (Test-Path $FileToCompile)) {
    Write-Host "FEHLER: Source-Datei nicht gefunden: $FileToCompile" -ForegroundColor Red
    exit 1
}

# Prüfe ob Include-Pfad existiert (Falls nicht, versuche Standard-Pfad)
if (-not (Test-Path $IncludePath)) {
    Write-Host "WARNUNG: Include-Pfad nicht gefunden, versuche Standard..." -ForegroundColor Yellow
    $IncludePath = "C:\Program Files\MetaTrader 5\MQL5"
    if (-not (Test-Path $IncludePath)) {
        Write-Host "WARNUNG: Auch Standard Include-Pfad nicht gefunden" -ForegroundColor Yellow
        $IncludePath = ""
    }
}

# Führe Kompilierung aus
Write-Host "Starte Kompilierung..." -ForegroundColor Green
& $CompileBat $MetaEditorPath $FileToCompile $LogFile $IncludePath

$ExitCode = $LASTEXITCODE
Write-Host "Exit Code: $ExitCode" -ForegroundColor $(if ($ExitCode -eq 0) { "Green" } else { "Red" })

# Prüfe Ergebnis
$Ex5File = $FileToCompile -replace '\.mq5$', '.ex5'
$Ex5Exists = Test-Path $Ex5File

Write-Host "EX5 Datei erstellt: $Ex5Exists" -ForegroundColor $(if ($Ex5Exists) { "Green" } else { "Red" })

# Zeige Log wenn vorhanden
if (Test-Path $LogFile) {
    Write-Host "`n=== COMPILE LOG ===" -ForegroundColor Cyan
    Get-Content $LogFile | Write-Host
} else {
    Write-Host "Keine Log-Datei erstellt" -ForegroundColor Yellow
}

# Rückgabe: 0 = Erfolg, 1 = Fehler
if ($Ex5Exists -and $ExitCode -eq 0) {
    Write-Host "`nKOMPILIERUNG ERFOLGREICH!" -ForegroundColor Green
    exit 0
} else {
    Write-Host "`nKOMPILIERUNG FEHLGESCHLAGEN!" -ForegroundColor Red
    exit 1
}
