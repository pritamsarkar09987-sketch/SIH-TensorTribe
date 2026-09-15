# IBVAP - Tactical Surveillance Platform Startup Script
Write-Host "==========================================================" -ForegroundColor Cyan
Write-Host " Starting IBVAP Decoupled Military Surveillance Platform  " -ForegroundColor Cyan
Write-Host "==========================================================" -ForegroundColor Cyan

# 1. Start Go Video Broadcaster
Write-Host "`n[1/4] Starting Go Video Broadcasting Service (Port 8080)..." -ForegroundColor Green
$goProcess = Start-Process -FilePath "D:\ibvap-workspace\SIH-TensorTribe\web-sockets\ibvap-go-broadcaster\ibvap-broadcaster.exe" -WorkingDirectory "D:\ibvap-workspace\SIH-TensorTribe\web-sockets\ibvap-go-broadcaster" -PassThru -WindowStyle Hidden
Write-Host "      Go Broadcaster running (PID: $($goProcess.Id))"

# 2. Start Node.js API
Write-Host "`n[2/4] Starting Node.js API & Database Service (Port 5000)..." -ForegroundColor Green
$nodeProcess = Start-Process -FilePath "node" -ArgumentList "backend/index.js" -WorkingDirectory "D:\ibvap-workspace\SIH-TensorTribe\ranajit-apis" -PassThru -WindowStyle Hidden
Write-Host "      Node.js API running (PID: $($nodeProcess.Id))"

# 3. Start Python AI Pipeline
Write-Host "`n[3/4] Starting Python AI YOLOv8 Streaming Pipeline (Port 8000)..." -ForegroundColor Green
$pythonExe = "D:\ibvap-workspace\venv\Scripts\python.exe"
$pyProcess = Start-Process -FilePath $pythonExe -ArgumentList "-m uvicorn main:app --port 8000 --host 127.0.0.1" -WorkingDirectory "D:\ibvap-workspace\SIH-TensorTribe\soumil-backend\backend" -PassThru -WindowStyle Hidden
Write-Host "      Python AI Pipeline running (PID: $($pyProcess.Id))"

# 4. Start React Frontend
Write-Host "`n[4/4] Starting React Command Dashboard (Port 5173)..." -ForegroundColor Green
$viteProcess = Start-Process -FilePath "npx" -ArgumentList "vite --port 5173 --host" -WorkingDirectory "D:\ibvap-workspace\SIH-TensorTribe\pritams-frontend" -PassThru -WindowStyle Hidden
Write-Host "      React Frontend running (PID: $($viteProcess.Id))"

Write-Host "`n----------------------------------------------------------" -ForegroundColor Yellow
Write-Host " All IBVAP Microservices are online and streaming!" -ForegroundColor Yellow
Write-Host " - Frontend Dashboard:   http://localhost:5173" -ForegroundColor White
Write-Host " - Go Broadcaster (WS):  ws://localhost:8080/stream" -ForegroundColor White
Write-Host " - Go Ingestion (HTTP):  http://localhost:8080/ingest" -ForegroundColor White
Write-Host " - Node.js Database API: http://localhost:5000/api" -ForegroundColor White
Write-Host " - Python AI Engine:     http://localhost:8000" -ForegroundColor White
Write-Host "----------------------------------------------------------" -ForegroundColor Yellow
