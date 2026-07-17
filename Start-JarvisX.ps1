$ErrorActionPreference = "Stop"

$Root = Split-Path -Parent $MyInvocation.MyCommand.Path
$Python = Join-Path $Root ".venv\Scripts\python.exe"
$AgentDir = Join-Path $Root "local-agent"

Set-Location $AgentDir
& $Python -m uvicorn app:app --reload --host 127.0.0.1 --port 8000
