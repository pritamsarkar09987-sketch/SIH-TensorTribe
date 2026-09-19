Write-Host "Stopping Netra AI Tactical Surveillance Platform..." -ForegroundColor Yellow
Get-NetTCPConnection -LocalPort 5000, 8000, 5173, 8080 -ErrorAction SilentlyContinue | ForEach-Object { Stop-Process -Id $_.OwningProcess -Force -ErrorAction SilentlyContinue }
Get-Process -Name "ibvap-broadcaster" -ErrorAction SilentlyContinue | Stop-Process -Force
Write-Host "All Netra AI microservices and servers stopped cleanly." -ForegroundColor Green
