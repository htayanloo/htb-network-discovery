@echo off
REM Makefile for Network Discovery Tool (Windows) - Using UV
REM Usage: make.bat <target>

setlocal enabledelayedexpansion

REM Variables
set UV=uv
set VENV=.venv
set VENV_PYTHON=%VENV%\Scripts\python.exe
set UV_RUN=%UV% run

REM Colors (for Windows 10+)
set RED=[91m
set GREEN=[92m
set YELLOW=[93m
set BLUE=[94m
set NC=[0m

REM Get command argument
set COMMAND=%1

if "%COMMAND%"=="" goto help
if "%COMMAND%"=="help" goto help
if "%COMMAND%"=="install-uv" goto install-uv
if "%COMMAND%"=="install" goto install
if "%COMMAND%"=="setup" goto install
if "%COMMAND%"=="venv" goto venv
if "%COMMAND%"=="deps" goto deps
if "%COMMAND%"=="package" goto package
if "%COMMAND%"=="sync" goto sync
if "%COMMAND%"=="config" goto config
if "%COMMAND%"=="discover" goto discover
if "%COMMAND%"=="discover-verbose" goto discover-verbose
if "%COMMAND%"=="discover-shallow" goto discover-shallow
if "%COMMAND%"=="status" goto status
if "%COMMAND%"=="list-devices" goto list-devices
if "%COMMAND%"=="list-switches" goto list-switches
if "%COMMAND%"=="list-connections" goto list-connections
if "%COMMAND%"=="stats" goto stats
if "%COMMAND%"=="search-mac" goto search-mac
if "%COMMAND%"=="search-device" goto search-device
if "%COMMAND%"=="export-json" goto export-json
if "%COMMAND%"=="export-graphml" goto export-graphml
if "%COMMAND%"=="export-all" goto export-all
if "%COMMAND%"=="serve" goto serve
if "%COMMAND%"=="serve-debug" goto serve-debug
if "%COMMAND%"=="serve-public" goto serve-public
if "%COMMAND%"=="db-init" goto db-init
if "%COMMAND%"=="db-backup" goto db-backup
if "%COMMAND%"=="db-clean" goto db-clean
if "%COMMAND%"=="shell" goto shell
if "%COMMAND%"=="test" goto test
if "%COMMAND%"=="lint" goto lint
if "%COMMAND%"=="format" goto format
if "%COMMAND%"=="clean" goto clean
if "%COMMAND%"=="clean-all" goto clean-all
if "%COMMAND%"=="quickstart" goto quickstart
if "%COMMAND%"=="uv-info" goto uv-info

echo %RED%Unknown command: %COMMAND%%NC%
goto help

:help
echo %BLUE%Network Discovery Tool - Windows Commands (UV-powered)%NC%
echo.
echo Usage: make.bat ^<target^>
echo.
echo %YELLOW%Setup:%NC%
echo   install-uv         Install uv package manager
echo   install            Full installation (create venv, install deps, setup config)
echo   setup              Alias for install
echo   venv               Create virtual environment with uv
echo   deps               Install dependencies with uv
echo   package            Install package in development mode
echo   sync               Sync dependencies (faster than reinstall)
echo   config             Create configuration files from templates
echo.
echo %YELLOW%Discovery:%NC%
echo   discover           Run network discovery
echo   discover-verbose   Run discovery with verbose logging
echo   discover-shallow   Run discovery with max depth 3
echo   status             Show last discovery status
echo.
echo %YELLOW%Data Management:%NC%
echo   list-devices       List all discovered devices
echo   list-switches      List all switches
echo   list-connections   List all connections
echo   stats              Show topology statistics
echo.
echo %YELLOW%Search:%NC%
echo   search-mac         Search for MAC address (set MAC=aa:bb:cc:dd:ee:ff)
echo   search-device      Search for device (set DEVICE=hostname)
echo.
echo %YELLOW%Export:%NC%
echo   export-json        Export topology as JSON
echo   export-graphml     Export topology as GraphML
echo   export-all         Export topology in all formats
echo.
echo %YELLOW%Web Server:%NC%
echo   serve              Start web dashboard server
echo   serve-debug        Start web server in debug mode
echo   serve-public       Start web server accessible from network
echo.
echo %YELLOW%Database:%NC%
echo   db-init            Initialize database
echo   db-backup          Backup database
echo   db-clean           Remove database (deletes all data!)
echo.
echo %YELLOW%Development:%NC%
echo   shell              Open Python shell with project context
echo   test               Run tests
echo   lint               Run linter
echo   format             Format code with black
echo   clean              Clean temporary files
echo   clean-all          Clean everything including database
echo.
echo %YELLOW%Utilities:%NC%
echo   uv-info            Show UV version and package info
echo.
echo %YELLOW%Quick Start:%NC%
echo   quickstart         Complete quickstart (install, discover, serve)
goto :eof

:install-uv
echo %BLUE%Checking for UV...%NC%
where uv >nul 2>&1
if %errorlevel% neq 0 (
    echo %YELLOW%UV not found. Installing...%NC%
    powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
    echo %GREEN%UV installed%NC%
) else (
    echo %GREEN%UV is already installed%NC%
)
uv --version
goto :eof

:install
echo %GREEN%Starting installation with UV...%NC%
call :install-uv
call :venv
call :deps
call :package
call :config
echo %GREEN%Installation complete!%NC%
echo.
echo %YELLOW%Next steps:%NC%
echo   1. Edit config\devices.yaml with your network details
echo   2. Set SSH password: set SSH_PASSWORD=your-password
echo   3. Run discovery: make.bat discover
goto :eof

:venv
echo %BLUE%Creating virtual environment with UV...%NC%
%UV% venv %VENV%
echo %GREEN%Virtual environment created%NC%
goto :eof

:deps
echo %BLUE%Installing dependencies with UV (ultra-fast!)...%NC%
%UV% pip install -r requirements.txt
echo %GREEN%Dependencies installed%NC%
goto :eof

:package
echo %BLUE%Installing package with UV...%NC%
%UV% pip install -e .
echo %GREEN%Package installed%NC%
goto :eof

:sync
echo %BLUE%Syncing dependencies with UV...%NC%
%UV% pip sync requirements.txt
echo %GREEN%Dependencies synced%NC%
goto :eof

:config
echo %BLUE%Setting up configuration...%NC%
if not exist config\devices.yaml (
    copy config\devices.yaml.example config\devices.yaml
    echo %GREEN%Created config\devices.yaml%NC%
    echo %YELLOW%Please edit config\devices.yaml with your network details%NC%
) else (
    echo %YELLOW%config\devices.yaml already exists%NC%
)
if not exist .env (
    copy .env.example .env
    echo %GREEN%Created .env%NC%
    echo %YELLOW%Please edit .env with your credentials%NC%
) else (
    echo %YELLOW%.env already exists%NC%
)
if not exist logs mkdir logs
echo %GREEN%Configuration setup complete%NC%
goto :eof

:discover
echo %BLUE%Starting network discovery...%NC%
%UV_RUN% network-discovery discover run
echo %GREEN%Discovery complete%NC%
goto :eof

:discover-verbose
echo %BLUE%Starting verbose network discovery...%NC%
set LOG_LEVEL=DEBUG
%UV_RUN% network-discovery discover run
echo %GREEN%Discovery complete%NC%
goto :eof

:discover-shallow
echo %BLUE%Starting shallow discovery (max depth 3)...%NC%
%UV_RUN% network-discovery discover run --max-depth 3
echo %GREEN%Discovery complete%NC%
goto :eof

:status
%UV_RUN% network-discovery discover status
goto :eof

:list-devices
%UV_RUN% network-discovery list-devices
goto :eof

:list-switches
%UV_RUN% network-discovery list-devices --type switch
goto :eof

:list-connections
%UV_RUN% network-discovery list-connections
goto :eof

:stats
%UV_RUN% network-discovery stats
goto :eof

:search-mac
if "%MAC%"=="" (
    echo %RED%Error: MAC address required%NC%
    echo Usage: set MAC=aa:bb:cc:dd:ee:ff ^&^& make.bat search-mac
    goto :eof
)
%UV_RUN% network-discovery search mac %MAC%
goto :eof

:search-device
if "%DEVICE%"=="" (
    echo %RED%Error: Device name required%NC%
    echo Usage: set DEVICE=hostname ^&^& make.bat search-device
    goto :eof
)
%UV_RUN% network-discovery search device %DEVICE%
goto :eof

:export-json
echo %BLUE%Exporting topology to topology.json...%NC%
%UV_RUN% network-discovery export --format json --output topology.json
echo %GREEN%Exported to topology.json%NC%
goto :eof

:export-graphml
echo %BLUE%Exporting topology to topology.graphml...%NC%
%UV_RUN% network-discovery export --format graphml --output topology.graphml
echo %GREEN%Exported to topology.graphml%NC%
goto :eof

:export-all
call :export-json
call :export-graphml
echo %GREEN%All exports complete%NC%
goto :eof

:serve
echo %BLUE%Starting web dashboard...%NC%
echo %GREEN%API: http://localhost:5000%NC%
echo %GREEN%Dashboard: Open web\index.html in your browser%NC%
echo %YELLOW%Press Ctrl+C to stop%NC%
%UV_RUN% network-discovery serve
goto :eof

:serve-debug
echo %BLUE%Starting web dashboard in debug mode...%NC%
%UV_RUN% network-discovery serve --debug
goto :eof

:serve-public
echo %BLUE%Starting web dashboard on 0.0.0.0:5000...%NC%
echo %YELLOW%Server will be accessible from your network%NC%
%UV_RUN% network-discovery serve --host 0.0.0.0 --port 5000
goto :eof

:db-init
echo %BLUE%Initializing database...%NC%
%UV_RUN% python -c "from src.database.schema import create_database; from src.utils.config import get_database_url; create_database(get_database_url())"
echo %GREEN%Database initialized%NC%
goto :eof

:db-backup
echo %BLUE%Backing up database...%NC%
for /f "tokens=2-4 delims=/ " %%a in ('date /t') do (set mydate=%%c%%a%%b)
for /f "tokens=1-2 delims=/:" %%a in ('time /t') do (set mytime=%%a%%b)
copy network_discovery.db network_discovery.db.backup.%mydate%_%mytime%
echo %GREEN%Database backed up%NC%
goto :eof

:db-clean
echo %RED%WARNING: This will delete all discovered data!%NC%
set /p confirm="Are you sure? (y/N): "
if /i not "%confirm%"=="y" goto :eof
del /f network_discovery.db 2>nul
echo %GREEN%Database removed%NC%
goto :eof

:shell
echo %BLUE%Opening Python shell...%NC%
%UV_RUN% python -i -c "from src.database.schema import *; from src.database.repository import *; from src.core.discovery.engine import *; from src.utils.config import *; print('Project modules loaded')"
goto :eof

:test
echo %BLUE%Running tests...%NC%
%UV_RUN% pytest tests\ -v
goto :eof

:lint
echo %BLUE%Running linter...%NC%
%UV_RUN% flake8 src\ --max-line-length=100 --ignore=E501,W503
goto :eof

:format
echo %BLUE%Formatting code...%NC%
%UV_RUN% black src\ --line-length=100
goto :eof

:clean
echo %BLUE%Cleaning temporary files...%NC%
for /d /r . %%d in (__pycache__) do @if exist "%%d" rd /s /q "%%d"
del /s /q *.pyc 2>nul
del /s /q *.pyo 2>nul
rd /s /q .pytest_cache 2>nul
rd /s /q .mypy_cache 2>nul
rd /s /q htmlcov 2>nul
del /q .coverage 2>nul
echo %GREEN%Temporary files cleaned%NC%
goto :eof

:clean-all
call :clean
echo %BLUE%Cleaning everything...%NC%
rd /s /q %VENV% 2>nul
del /q topology.json 2>nul
del /q topology.graphml 2>nul
del /q topology.gexf 2>nul
del /q logs\*.log 2>nul
del /q network_discovery.db 2>nul
del /q uv.lock 2>nul
echo %GREEN%Everything cleaned%NC%
goto :eof

:uv-info
echo %BLUE%UV Information:%NC%
%UV% --version
echo.
%UV% pip list
goto :eof

:quickstart
call :install
call :discover
call :serve
goto :eof

:eof
endlocal
