# PowerShell Makefile for Network Discovery Tool (Windows)
# Usage: .\make.ps1 <target>

param(
    [Parameter(Position=0)]
    [string]$Command = "help",

    [Parameter(ValueFromRemainingArguments=$true)]
    [string[]]$Args
)

# Variables
$PYTHON = "python"
$VENV = "venv"
$VENV_PYTHON = "$VENV\Scripts\python.exe"
$VENV_PIP = "$VENV\Scripts\pip.exe"
$NETWORK_DISCOVERY = "$VENV\Scripts\network-discovery.exe"

# Colors
function Write-ColorOutput {
    param(
        [string]$Message,
        [string]$Color = "White"
    )
    Write-Host $Message -ForegroundColor $Color
}

function Show-Help {
    Write-ColorOutput "Network Discovery Tool - PowerShell Commands" "Blue"
    Write-Host ""
    Write-Host "Usage: .\make.ps1 <target>"
    Write-Host ""
    Write-ColorOutput "Setup:" "Yellow"
    Write-Host "  install            Full installation (create venv, install deps, setup config)"
    Write-Host "  setup              Alias for install"
    Write-Host "  venv               Create virtual environment"
    Write-Host "  deps               Install dependencies"
    Write-Host "  package            Install package in development mode"
    Write-Host "  config             Create configuration files from templates"
    Write-Host ""
    Write-ColorOutput "Discovery:" "Yellow"
    Write-Host "  discover           Run network discovery"
    Write-Host "  discover-verbose   Run discovery with verbose logging"
    Write-Host "  discover-shallow   Run discovery with max depth 3"
    Write-Host "  status             Show last discovery status"
    Write-Host ""
    Write-ColorOutput "Data Management:" "Yellow"
    Write-Host "  list-devices       List all discovered devices"
    Write-Host "  list-switches      List all switches"
    Write-Host "  list-connections   List all connections"
    Write-Host "  stats              Show topology statistics"
    Write-Host ""
    Write-ColorOutput "Search:" "Yellow"
    Write-Host "  search-mac         Search for MAC address"
    Write-Host "                     Usage: .\make.ps1 search-mac aa:bb:cc:dd:ee:ff"
    Write-Host "  search-device      Search for device"
    Write-Host "                     Usage: .\make.ps1 search-device hostname"
    Write-Host ""
    Write-ColorOutput "Export:" "Yellow"
    Write-Host "  export-json        Export topology as JSON"
    Write-Host "  export-graphml     Export topology as GraphML"
    Write-Host "  export-all         Export topology in all formats"
    Write-Host ""
    Write-ColorOutput "Web Server:" "Yellow"
    Write-Host "  serve              Start web dashboard server"
    Write-Host "  serve-debug        Start web server in debug mode"
    Write-Host "  serve-public       Start web server accessible from network"
    Write-Host ""
    Write-ColorOutput "Database:" "Yellow"
    Write-Host "  db-init            Initialize database"
    Write-Host "  db-backup          Backup database"
    Write-Host "  db-clean           Remove database (deletes all data!)"
    Write-Host ""
    Write-ColorOutput "Development:" "Yellow"
    Write-Host "  shell              Open Python shell with project context"
    Write-Host "  test               Run tests"
    Write-Host "  lint               Run linter"
    Write-Host "  format             Format code with black"
    Write-Host "  clean              Clean temporary files"
    Write-Host "  clean-all          Clean everything including database"
    Write-Host ""
    Write-ColorOutput "Quick Start:" "Yellow"
    Write-Host "  quickstart         Complete quickstart (install, discover, serve)"
}

function Install-Project {
    Write-ColorOutput "Starting installation..." "Green"
    Create-Venv
    Install-Deps
    Install-Package
    Setup-Config
    Write-ColorOutput "Installation complete!" "Green"
    Write-Host ""
    Write-ColorOutput "Next steps:" "Yellow"
    Write-Host "  1. Edit config\devices.yaml with your network details"
    Write-Host "  2. Set SSH password: `$env:SSH_PASSWORD='your-password'"
    Write-Host "  3. Run discovery: .\make.ps1 discover"
}

function Create-Venv {
    Write-ColorOutput "Creating virtual environment..." "Blue"
    if (-not (Test-Path $VENV)) {
        & $PYTHON -m venv $VENV
        Write-ColorOutput "✓ Virtual environment created" "Green"
    } else {
        Write-ColorOutput "⚠ Virtual environment already exists" "Yellow"
    }
}

function Install-Deps {
    Write-ColorOutput "Installing dependencies..." "Blue"
    & $VENV_PIP install --upgrade pip setuptools wheel
    & $VENV_PIP install -r requirements.txt
    Write-ColorOutput "✓ Dependencies installed" "Green"
}

function Install-Package {
    Write-ColorOutput "Installing package..." "Blue"
    & $VENV_PIP install -e .
    Write-ColorOutput "✓ Package installed" "Green"
}

function Setup-Config {
    Write-ColorOutput "Setting up configuration..." "Blue"

    if (-not (Test-Path "config\devices.yaml")) {
        Copy-Item "config\devices.yaml.example" "config\devices.yaml"
        Write-ColorOutput "✓ Created config\devices.yaml" "Green"
        Write-ColorOutput "⚠ Please edit config\devices.yaml with your network details" "Yellow"
    } else {
        Write-ColorOutput "⚠ config\devices.yaml already exists" "Yellow"
    }

    if (-not (Test-Path ".env")) {
        Copy-Item ".env.example" ".env"
        Write-ColorOutput "✓ Created .env" "Green"
        Write-ColorOutput "⚠ Please edit .env with your credentials" "Yellow"
    } else {
        Write-ColorOutput "⚠ .env already exists" "Yellow"
    }

    if (-not (Test-Path "logs")) {
        New-Item -ItemType Directory -Path "logs" | Out-Null
    }

    Write-ColorOutput "✓ Configuration setup complete" "Green"
}

function Run-Discovery {
    Write-ColorOutput "Starting network discovery..." "Blue"
    & $NETWORK_DISCOVERY discover run
    Write-ColorOutput "✓ Discovery complete" "Green"
}

function Run-DiscoveryVerbose {
    Write-ColorOutput "Starting verbose network discovery..." "Blue"
    $env:LOG_LEVEL = "DEBUG"
    & $NETWORK_DISCOVERY discover run
    Write-ColorOutput "✓ Discovery complete" "Green"
}

function Run-DiscoveryShallow {
    Write-ColorOutput "Starting shallow discovery (max depth 3)..." "Blue"
    & $NETWORK_DISCOVERY discover run --max-depth 3
    Write-ColorOutput "✓ Discovery complete" "Green"
}

function Show-Status {
    & $NETWORK_DISCOVERY discover status
}

function List-Devices {
    & $NETWORK_DISCOVERY list-devices
}

function List-Switches {
    & $NETWORK_DISCOVERY list-devices --type switch
}

function List-Connections {
    & $NETWORK_DISCOVERY list-connections
}

function Show-Stats {
    & $NETWORK_DISCOVERY stats
}

function Search-MAC {
    param([string]$MAC)

    if (-not $MAC) {
        if ($Args.Count -gt 0) {
            $MAC = $Args[0]
        } else {
            Write-ColorOutput "Error: MAC address required" "Red"
            Write-Host "Usage: .\make.ps1 search-mac aa:bb:cc:dd:ee:ff"
            return
        }
    }

    & $NETWORK_DISCOVERY search mac $MAC
}

function Search-Device {
    param([string]$Device)

    if (-not $Device) {
        if ($Args.Count -gt 0) {
            $Device = $Args[0]
        } else {
            Write-ColorOutput "Error: Device name required" "Red"
            Write-Host "Usage: .\make.ps1 search-device hostname"
            return
        }
    }

    & $NETWORK_DISCOVERY search device $Device
}

function Export-JSON {
    Write-ColorOutput "Exporting topology to topology.json..." "Blue"
    & $NETWORK_DISCOVERY export --format json --output topology.json
    Write-ColorOutput "✓ Exported to topology.json" "Green"
}

function Export-GraphML {
    Write-ColorOutput "Exporting topology to topology.graphml..." "Blue"
    & $NETWORK_DISCOVERY export --format graphml --output topology.graphml
    Write-ColorOutput "✓ Exported to topology.graphml" "Green"
}

function Export-All {
    Export-JSON
    Export-GraphML
    Write-ColorOutput "✓ All exports complete" "Green"
}

function Start-Server {
    Write-ColorOutput "Starting web dashboard..." "Blue"
    Write-ColorOutput "API: http://localhost:5000" "Green"
    Write-ColorOutput "Dashboard: Open web\index.html in your browser" "Green"
    Write-ColorOutput "Press Ctrl+C to stop" "Yellow"
    & $NETWORK_DISCOVERY serve
}

function Start-ServerDebug {
    Write-ColorOutput "Starting web dashboard in debug mode..." "Blue"
    & $NETWORK_DISCOVERY serve --debug
}

function Start-ServerPublic {
    Write-ColorOutput "Starting web dashboard on 0.0.0.0:5000..." "Blue"
    Write-ColorOutput "Server will be accessible from your network" "Yellow"
    & $NETWORK_DISCOVERY serve --host 0.0.0.0 --port 5000
}

function Initialize-DB {
    Write-ColorOutput "Initializing database..." "Blue"
    & $VENV_PYTHON -c "from src.database.schema import create_database; from src.utils.config import get_database_url; create_database(get_database_url())"
    Write-ColorOutput "✓ Database initialized" "Green"
}

function Backup-DB {
    Write-ColorOutput "Backing up database..." "Blue"
    $timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
    Copy-Item "network_discovery.db" "network_discovery.db.backup.$timestamp"
    Write-ColorOutput "✓ Database backed up" "Green"
}

function Clean-DB {
    Write-ColorOutput "WARNING: This will delete all discovered data!" "Red"
    $confirm = Read-Host "Are you sure? (y/N)"

    if ($confirm -eq "y" -or $confirm -eq "Y") {
        Remove-Item "network_discovery.db" -ErrorAction SilentlyContinue
        Write-ColorOutput "✓ Database removed" "Green"
    } else {
        Write-Host "Cancelled"
    }
}

function Open-Shell {
    Write-ColorOutput "Opening Python shell..." "Blue"
    & $VENV_PYTHON -i -c "from src.database.schema import *; from src.database.repository import *; from src.core.discovery.engine import *; from src.utils.config import *; print('Project modules loaded')"
}

function Run-Tests {
    Write-ColorOutput "Running tests..." "Blue"
    & "$VENV\Scripts\pytest" tests\ -v
}

function Run-Lint {
    Write-ColorOutput "Running linter..." "Blue"
    & "$VENV\Scripts\flake8" src\ --max-line-length=100 --ignore=E501,W503
}

function Run-Format {
    Write-ColorOutput "Formatting code..." "Blue"
    & "$VENV\Scripts\black" src\ --line-length=100
}

function Clean-Temp {
    Write-ColorOutput "Cleaning temporary files..." "Blue"
    Get-ChildItem -Path . -Recurse -Directory -Filter "__pycache__" | Remove-Item -Recurse -Force -ErrorAction SilentlyContinue
    Get-ChildItem -Path . -Recurse -File -Filter "*.pyc" | Remove-Item -Force -ErrorAction SilentlyContinue
    Get-ChildItem -Path . -Recurse -File -Filter "*.pyo" | Remove-Item -Force -ErrorAction SilentlyContinue
    Remove-Item -Path ".pytest_cache" -Recurse -Force -ErrorAction SilentlyContinue
    Remove-Item -Path ".mypy_cache" -Recurse -Force -ErrorAction SilentlyContinue
    Remove-Item -Path "htmlcov" -Recurse -Force -ErrorAction SilentlyContinue
    Remove-Item -Path ".coverage" -Force -ErrorAction SilentlyContinue
    Write-ColorOutput "✓ Temporary files cleaned" "Green"
}

function Clean-All {
    Clean-Temp
    Write-ColorOutput "Cleaning everything..." "Blue"
    Remove-Item -Path $VENV -Recurse -Force -ErrorAction SilentlyContinue
    Remove-Item -Path "topology.json" -Force -ErrorAction SilentlyContinue
    Remove-Item -Path "topology.graphml" -Force -ErrorAction SilentlyContinue
    Remove-Item -Path "topology.gexf" -Force -ErrorAction SilentlyContinue
    Remove-Item -Path "logs\*.log" -Force -ErrorAction SilentlyContinue
    Remove-Item -Path "network_discovery.db" -Force -ErrorAction SilentlyContinue
    Write-ColorOutput "✓ Everything cleaned" "Green"
}

function Run-Quickstart {
    Install-Project
    Run-Discovery
    Start-Server
}

# Main command dispatcher
switch ($Command.ToLower()) {
    "help" { Show-Help }
    "install" { Install-Project }
    "setup" { Install-Project }
    "venv" { Create-Venv }
    "deps" { Install-Deps }
    "package" { Install-Package }
    "config" { Setup-Config }
    "discover" { Run-Discovery }
    "discover-verbose" { Run-DiscoveryVerbose }
    "discover-shallow" { Run-DiscoveryShallow }
    "status" { Show-Status }
    "list-devices" { List-Devices }
    "list-switches" { List-Switches }
    "list-connections" { List-Connections }
    "stats" { Show-Stats }
    "search-mac" { Search-MAC -MAC $Args }
    "search-device" { Search-Device -Device $Args }
    "export-json" { Export-JSON }
    "export-graphml" { Export-GraphML }
    "export-all" { Export-All }
    "serve" { Start-Server }
    "serve-debug" { Start-ServerDebug }
    "serve-public" { Start-ServerPublic }
    "db-init" { Initialize-DB }
    "db-backup" { Backup-DB }
    "db-clean" { Clean-DB }
    "shell" { Open-Shell }
    "test" { Run-Tests }
    "lint" { Run-Lint }
    "format" { Run-Format }
    "clean" { Clean-Temp }
    "clean-all" { Clean-All }
    "quickstart" { Run-Quickstart }
    default {
        Write-ColorOutput "Unknown command: $Command" "Red"
        Show-Help
    }
}
