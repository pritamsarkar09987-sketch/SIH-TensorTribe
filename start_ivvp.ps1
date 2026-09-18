# IVVP - Intelligent Border Video Analytics Platform (Consolidated Single Entry Point)
Write-Host "==========================================================" -ForegroundColor Cyan
Write-Host " Starting IVVP Consolidated Tactical Surveillance Platform" -ForegroundColor Cyan
Write-Host "==========================================================" -ForegroundColor Cyan

# 0. Clean up any existing stale processes
Write-Host "Cleaning up previous instances..." -ForegroundColor Yellow
Get-NetTCPConnection -LocalPort 5000, 8000, 5173, 8080 -ErrorAction SilentlyContinue | ForEach-Object { Stop-Process -Id $_.OwningProcess -Force -ErrorAction SilentlyContinue }
Get-Process -Name "ibvap-broadcaster" -ErrorAction SilentlyContinue | Stop-Process -Force
Get-Process -Name "python" -ErrorAction SilentlyContinue | Where-Object { $_.Path -like "*ibvap-workspace*" } | Stop-Process -Force

function Start-DetachedProcess {
    param(
        [string]$FilePath,
        [string]$ArgumentList = "",
        [string]$WorkingDirectory = ""
    )
    $cmd = if ($ArgumentList) { "`"$FilePath`" $ArgumentList" } else { "`"$FilePath`"" }
    try {
        $res = Invoke-CimMethod -ClassName Win32_Process -MethodName Create -Arguments @{
            CommandLine = $cmd
            CurrentDirectory = $WorkingDirectory
        } -ErrorAction Stop
        return $res.ProcessId
    } catch {
        $proc = Start-Process -FilePath $FilePath -ArgumentList $ArgumentList -WorkingDirectory $WorkingDirectory -PassThru -WindowStyle Hidden
        return $proc.Id
    }
}

# 1. Start Python AI Computer Vision Engine (+10M Perimeter ROI & YOLOv8)
Write-Host "`n[1/2] Starting Python AI YOLOv8 Streaming Pipeline (Port 8000)..." -ForegroundColor Green
$pythonExe = "D:\ibvap-workspace\venv\Scripts\python.exe"
$pyPid = Start-DetachedProcess -FilePath $pythonExe -ArgumentList "-m uvicorn main:app --port 8000 --host 127.0.0.1" -WorkingDirectory "$PSScriptRoot\soumil-backend\backend"
Write-Host "      Python AI Engine starting (PID: $pyPid)..."

# 2. Start Consolidated Monolith Server (Port 5000: Dashboard + WebSockets + APIs)
Write-Host "`n[2/2] Starting Consolidated Monolith Server (Port 5000)..." -ForegroundColor Green
$nodePid = Start-DetachedProcess -FilePath "node" -ArgumentList "backend/index.js" -WorkingDirectory "$PSScriptRoot\ranajit-apis"
Write-Host "      Consolidated Monolith Server starting (PID: $nodePid)..."

# 3. Verify Health with Dynamic Polling (allow PyTorch DLLs to warm up)
Write-Host "`nVerifying platform health status (polling ports 5000 & 8000)..." -ForegroundColor Cyan
$maxSeconds = 12
$port5000Online = $false
$port8000Online = $false

for ($i = 0; $i -lt $maxSeconds; $i++) {
    Start-Sleep -Seconds 1
    if (-not $port5000Online -and (Get-NetTCPConnection -LocalPort 5000 -State Listen -ErrorAction SilentlyContinue)) {
        $port5000Online = $true
    }
    if (-not $port8000Online -and (Get-NetTCPConnection -LocalPort 8000 -State Listen -ErrorAction SilentlyContinue)) {
        $port8000Online = $true
    }
    if ($port5000Online -and $port8000Online) {
        break
    }
}

Write-Host "`n==========================================================" -ForegroundColor Yellow
Write-Host " IVVP Unified Monolith Status:" -ForegroundColor Yellow
if ($port5000Online) {
    Write-Host " [ONLINE]  Consolidated Access Point: http://localhost:5000" -ForegroundColor Green
    Write-Host "           - Web Dashboard UI:       http://localhost:5000" -ForegroundColor White
    Write-Host "           - WebSocket Video Feed:   ws://localhost:5000/stream" -ForegroundColor White
    Write-Host "           - Frame Ingestion:        http://localhost:5000/ingest" -ForegroundColor White
    Write-Host "           - REST API:               http://localhost:5000/api" -ForegroundColor White
} else {
    Write-Host " [OFFLINE] Consolidated Server on Port 5000 (Check database connection in .env)" -ForegroundColor Red
}

if ($port8000Online) {
    Write-Host " [ONLINE]  Computer Vision Engine:    http://localhost:8000" -ForegroundColor Green
    Write-Host "           - Detection:              YOLOv8 Person Model" -ForegroundColor White
    Write-Host "           - ROI Perimeter:          +10M Static Yellow Bracket" -ForegroundColor White
    Write-Host "           - Automated Alerting:     Email Dispatch on Breach" -ForegroundColor White
} else {
    Write-Host " [OFFLINE] Python AI Engine on Port 8000" -ForegroundColor Red
}
Write-Host "==========================================================" -ForegroundColor Yellow
Write-Host "`n>> All services online. Open http://localhost:5000 in your browser! <<`n" -ForegroundColor Cyan
