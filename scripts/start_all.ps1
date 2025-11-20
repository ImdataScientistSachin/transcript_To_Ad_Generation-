<#
Start Redis, worker (containerized or local), and Streamlit for development.

Usage:
  .\scripts\start_all.ps1                       # start Redis, start Streamlit and local worker in new windows
  .\scripts\start_all.ps1 -ContainerWorker      # start Redis and worker inside Docker, Streamlit locally

#>

param(
    [switch]$ContainerWorker
)

function Write-Info($m) { Write-Host "[info] $m" -ForegroundColor Cyan }
function Write-OK($m) { Write-Host "[ok]   $m" -ForegroundColor Green }

$dockerExists = (Get-Command docker -ErrorAction SilentlyContinue) -ne $null
if (-not $dockerExists) {
    Write-Host "Docker is required to start Redis. Install Docker Desktop or run Redis separately." -ForegroundColor Yellow
    exit 1
}

Write-Info "Starting Redis via docker compose..."
docker compose up -d redis

Write-Info "Waiting for Redis on localhost:6379..."
$deadline = (Get-Date).AddSeconds(30)
$reachable = $false
while ((Get-Date) -lt $deadline) {
    $res = Test-NetConnection -ComputerName 'localhost' -Port 6379 -WarningAction SilentlyContinue
    if ($res -and $res.TcpTestSucceeded) { $reachable = $true; break }
    Start-Sleep -Seconds 1
}
if (-not $reachable) {
    Write-Host "Warning: Redis not reachable after 30s. Check docker logs." -ForegroundColor Yellow
} else { Write-OK "Redis is reachable." }

if ($ContainerWorker) {
    Write-Info "Starting worker in container (docker compose up worker)..."
    docker compose up -d --build worker
    Write-OK "Worker container started. View logs with: docker logs -f transcript_to_ad_worker"
} else {
    Write-Info "Starting local worker in a new PowerShell window..."
    Start-Process powershell -ArgumentList @('-NoExit','-Command','python .\scripts\worker.py') -WorkingDirectory (Get-Location)
    Start-Sleep -Seconds 1
}

Write-Info "Starting Streamlit in a new PowerShell window..."
Start-Process powershell -ArgumentList @('-NoExit','-Command','streamlit run app.py') -WorkingDirectory (Get-Location)

Write-OK "All services started. Use Ctrl+C in the opened worker/streamlit windows to stop those processes. To stop containers: docker compose down"
