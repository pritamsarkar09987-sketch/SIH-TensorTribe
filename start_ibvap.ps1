# Netra AI - Decoupled Military Surveillance Platform
Write-Host "==========================================================" -ForegroundColor Cyan
Write-Host " Starting Netra AI Tactical Surveillance Platform" -ForegroundColor Cyan
Write-Host "==========================================================" -ForegroundColor Cyan

# Clean up any existing stale processes
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

# Start Python AI computer vision engine
Write-Host "`n[1/2] Starting Python AI YOLOv8 Streaming Pipeline (Port 8000)..." -ForegroundColor Green
$pythonExe = "D:\ibvap-workspace\venv\Scripts\python.exe"
$pyPid = Start-DetachedProcess -FilePath $pythonExe -ArgumentList "-m uvicorn main:app --port 8000 --host 127.0.0.1" -WorkingDirectory "$PSScriptRoot\soumil-backend\backend"
Write-Host "      Python AI Engine starting (PID: $pyPid)..."

# Start Node.js API and database server
Write-Host "`n[2/2] Starting API and Database Server (Port 5000)..." -ForegroundColor Green
$nodePid = Start-DetachedProcess -FilePath "node" -ArgumentList "backend/index.js" -WorkingDirectory "$PSScriptRoot\ranajit-apis"
Write-Host "      API and Database Server starting (PID: $nodePid)..."

# Verify health with dynamic polling
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
Write-Host " Netra AI Platform Status:" -ForegroundColor Yellow
if ($port5000Online) {
	Write-Host " [ONLINE]  Command Center & API Access: http://localhost:5000" -ForegroundColor Green
} else {
	Write-Host " [OFFLINE] API Server on Port 5000 (Check database connection in .env)" -ForegroundColor Red
}

if ($port8000Online) {
	Write-Host " [ONLINE]  Netra AI Computer Vision Engine: http://localhost:8000" -ForegroundColor Green
} else {
	Write-Host " [OFFLINE] Netra AI Python Engine on Port 8000" -ForegroundColor Red
}
Write-Host "==========================================================" -ForegroundColor Yellow
Write-Host "`n>> Platform startup complete. <<`n" -ForegroundColor Cyan
