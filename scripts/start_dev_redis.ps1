<#
Start Dev Redis + Worker helper

Usage:
  .\scripts\start_dev_redis.ps1            # uses docker-compose.yml if present
  .\scripts\start_dev_redis.ps1 -TimeoutSeconds 60

This script will start a local Redis container (via docker-compose or docker run),
wait for the port to become reachable, then run the local worker: `python scripts/worker.py`.
#>

param(
    [int]$TimeoutSeconds = 30
)

function Write-Info($m) { Write-Host "[info] $m" -ForegroundColor Cyan }
function Write-OK($m) { Write-Host "[ok]   $m" -ForegroundColor Green }

$dockerExists = (Get-Command docker -ErrorAction SilentlyContinue) -ne $null
if (-not $dockerExists) {
    Write-Host "Docker is required to run Redis locally. Install Docker Desktop or provide REDIS_URL." -ForegroundColor Yellow
    exit 1
}

$composeFile = Join-Path (Get-Location) 'docker-compose.yml'
if (Test-Path $composeFile) {
    Write-Info "Starting Redis via docker-compose..."
    # prefer `docker compose` plugin if docker-compose is not available
    if (Get-Command docker-compose -ErrorAction SilentlyContinue) {
        docker-compose up -d redis
    } else {
        docker compose up -d redis
    }
} else {
    Write-Info "docker-compose.yml not found — starting Redis via 'docker run'..."
    docker run -d --name transcript_to_ad_redis -p 6379:6379 redis:7-alpine
}

Write-Info "Waiting for Redis to accept connections on localhost:6379 (timeout ${TimeoutSeconds}s)..."
$deadline = (Get-Date).AddSeconds($TimeoutSeconds)
$reachable = $false
while ((Get-Date) -lt $deadline) {
    $res = Test-NetConnection -ComputerName 'localhost' -Port 6379 -WarningAction SilentlyContinue
    if ($res -and $res.TcpTestSucceeded) {
        $reachable = $true
        break
    }
    Start-Sleep -Seconds 1
}

if ($reachable) {
    Write-OK "Redis is reachable on localhost:6379"
} else {
    Write-Host "Warning: Redis did not become reachable within $TimeoutSeconds seconds." -ForegroundColor Yellow
    Write-Host "You can still start the worker after starting Redis." -ForegroundColor Yellow
}

Write-Info "Starting local worker: python scripts/worker.py"
try {
    python .\scripts\worker.py
} catch {
    Write-Host "Failed to start worker: $_" -ForegroundColor Red
    exit 1
}
