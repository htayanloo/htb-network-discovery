# Makefile Guide

This project includes build automation files for both Linux/macOS and Windows to simplify setup and running tasks.

## Available Files

- **Makefile** - For Linux/macOS (requires `make`)
- **make.bat** - For Windows (batch file, works in cmd.exe)
- **make.ps1** - For Windows (PowerShell script, more advanced)

## Quick Start

### Linux/macOS

```bash
# Show all available commands
make help

# Complete installation
make install

# Run discovery
make discover

# Start web server
make serve
```

### Windows (Command Prompt)

```cmd
REM Show all available commands
make.bat help

REM Complete installation
make.bat install

REM Run discovery
make.bat discover

REM Start web server
make.bat serve
```

### Windows (PowerShell)

```powershell
# Show all available commands
.\make.ps1 help

# Complete installation
.\make.ps1 install

# Run discovery
.\make.ps1 discover

# Start web server
.\make.ps1 serve
```

## Common Commands

### Setup Commands

| Command | Description |
|---------|-------------|
| `install` | Full installation (venv, dependencies, config) |
| `setup` | Alias for install |
| `venv` | Create virtual environment only |
| `deps` | Install dependencies only |
| `package` | Install package in development mode |
| `config` | Create configuration files from templates |

#### Examples

**Linux/macOS:**
```bash
make install          # Complete installation
make venv             # Just create venv
make deps             # Just install dependencies
```

**Windows (cmd):**
```cmd
make.bat install      # Complete installation
make.bat venv         # Just create venv
make.bat deps         # Just install dependencies
```

**Windows (PowerShell):**
```powershell
.\make.ps1 install    # Complete installation
.\make.ps1 venv       # Just create venv
.\make.ps1 deps       # Just install dependencies
```

### Discovery Commands

| Command | Description |
|---------|-------------|
| `discover` | Run network discovery |
| `discover-verbose` | Run discovery with DEBUG logging |
| `discover-shallow` | Run discovery with max depth 3 |
| `status` | Show last discovery session status |

#### Examples

**Linux/macOS:**
```bash
make discover                  # Normal discovery
make discover-verbose          # Verbose discovery
make discover-shallow          # Shallow discovery
make status                    # Check status
```

**Windows:**
```cmd
make.bat discover              # Normal discovery
make.bat discover-verbose      # Verbose discovery
make.bat discover-shallow      # Shallow discovery
make.bat status                # Check status
```

### Data Management Commands

| Command | Description |
|---------|-------------|
| `list-devices` | List all discovered devices |
| `list-switches` | List only switches |
| `list-connections` | List all connections |
| `stats` | Show topology statistics |

#### Examples

**Linux/macOS:**
```bash
make list-devices              # List all devices
make list-switches             # List switches only
make list-connections          # List connections
make stats                     # Show statistics
```

**Windows:**
```cmd
make.bat list-devices          # List all devices
make.bat list-switches         # List switches only
make.bat list-connections      # List connections
make.bat stats                 # Show statistics
```

### Search Commands

| Command | Description |
|---------|-------------|
| `search-mac` | Search for MAC address |
| `search-device` | Search for device by hostname/IP |

#### Examples

**Linux/macOS:**
```bash
make search-mac MAC=aa:bb:cc:dd:ee:ff
make search-device DEVICE=CORE-SW-01
make search-device DEVICE=192.168.1.1
```

**Windows (cmd):**
```cmd
set MAC=aa:bb:cc:dd:ee:ff
make.bat search-mac

set DEVICE=CORE-SW-01
make.bat search-device
```

**Windows (PowerShell):**
```powershell
.\make.ps1 search-mac aa:bb:cc:dd:ee:ff
.\make.ps1 search-device CORE-SW-01
.\make.ps1 search-device 192.168.1.1
```

### Export Commands

| Command | Description |
|---------|-------------|
| `export-json` | Export topology as JSON |
| `export-graphml` | Export topology as GraphML |
| `export-all` | Export in all formats |

#### Examples

**Linux/macOS:**
```bash
make export-json               # Export to topology.json
make export-graphml            # Export to topology.graphml
make export-all                # Export all formats
```

**Windows:**
```cmd
make.bat export-json           # Export to topology.json
make.bat export-graphml        # Export to topology.graphml
make.bat export-all            # Export all formats
```

### Web Server Commands

| Command | Description |
|---------|-------------|
| `serve` | Start web dashboard (localhost:5000) |
| `serve-debug` | Start in debug mode |
| `serve-public` | Start on 0.0.0.0 (accessible from network) |

#### Examples

**Linux/macOS:**
```bash
make serve                     # Start server
make serve-debug               # Debug mode
make serve-public              # Public access
```

**Windows:**
```cmd
make.bat serve                 # Start server
make.bat serve-debug           # Debug mode
make.bat serve-public          # Public access
```

### Database Commands

| Command | Description |
|---------|-------------|
| `db-init` | Initialize database |
| `db-backup` | Backup database |
| `db-clean` | Remove database (WARNING: deletes all data!) |

#### Examples

**Linux/macOS:**
```bash
make db-init                   # Initialize database
make db-backup                 # Backup database
make db-clean                  # Clean database (prompts for confirmation)
```

**Windows:**
```cmd
make.bat db-init               # Initialize database
make.bat db-backup             # Backup database
make.bat db-clean              # Clean database (prompts for confirmation)
```

### Development Commands

| Command | Description |
|---------|-------------|
| `shell` | Open Python shell with project context |
| `test` | Run tests |
| `lint` | Run linter (flake8) |
| `format` | Format code (black) |
| `clean` | Clean temporary files |
| `clean-all` | Clean everything including venv and database |

#### Examples

**Linux/macOS:**
```bash
make shell                     # Open Python shell
make test                      # Run tests
make lint                      # Lint code
make format                    # Format code
make clean                     # Clean temp files
make clean-all                 # Clean everything
```

**Windows:**
```cmd
make.bat shell                 # Open Python shell
make.bat test                  # Run tests
make.bat lint                  # Lint code
make.bat format                # Format code
make.bat clean                 # Clean temp files
make.bat clean-all             # Clean everything
```

### Quick Start Command

| Command | Description |
|---------|-------------|
| `quickstart` | Install, discover, and start server |

This command runs the complete workflow:
1. Install dependencies
2. Setup configuration
3. Run discovery
4. Start web server

**Linux/macOS:**
```bash
make quickstart
```

**Windows:**
```cmd
make.bat quickstart
```

**PowerShell:**
```powershell
.\make.ps1 quickstart
```

## Complete Workflow Examples

### First Time Setup

**Linux/macOS:**
```bash
# 1. Install everything
make install

# 2. Edit configuration
nano config/devices.yaml

# 3. Set SSH password
export SSH_PASSWORD="your-password"

# 4. Run discovery
make discover

# 5. View results
make list-devices
make stats

# 6. Start web dashboard
make serve
```

**Windows (PowerShell):**
```powershell
# 1. Install everything
.\make.ps1 install

# 2. Edit configuration
notepad config\devices.yaml

# 3. Set SSH password
$env:SSH_PASSWORD = "your-password"

# 4. Run discovery
.\make.ps1 discover

# 5. View results
.\make.ps1 list-devices
.\make.ps1 stats

# 6. Start web dashboard
.\make.ps1 serve
```

### Daily Usage

**Linux/macOS:**
```bash
# Run daily discovery
make discover

# Check what changed
make stats
make list-devices

# Search for something
make search-mac MAC=00:11:22:33:44:55

# Export data
make export-all

# Backup database
make db-backup
```

**Windows:**
```cmd
REM Run daily discovery
make.bat discover

REM Check what changed
make.bat stats
make.bat list-devices

REM Search for something
set MAC=00:11:22:33:44:55
make.bat search-mac

REM Export data
make.bat export-all

REM Backup database
make.bat db-backup
```

### Development Workflow

**Linux/macOS:**
```bash
# Make code changes
# ...

# Format code
make format

# Run linter
make lint

# Run tests
make test

# Test discovery
make discover-verbose

# Clean up
make clean
```

**Windows:**
```cmd
REM Make code changes
REM ...

REM Format code
make.bat format

REM Run linter
make.bat lint

REM Run tests
make.bat test

REM Test discovery
make.bat discover-verbose

REM Clean up
make.bat clean
```

## Troubleshooting

### Linux/macOS Issues

**Problem: `make: command not found`**

Solution:
```bash
# Install make
# Ubuntu/Debian
sudo apt-get install build-essential

# macOS (should be pre-installed, if not)
xcode-select --install
```

**Problem: Virtual environment not activating**

Solution:
```bash
# The Makefile handles venv automatically
# But if you need to activate manually:
source venv/bin/activate
```

### Windows Issues

**Problem: `make.bat is not recognized`**

Solution:
```cmd
REM Use full path
C:\path\to\project\make.bat install

REM Or navigate to project directory first
cd C:\path\to\project
make.bat install
```

**Problem: PowerShell execution policy error**

Solution:
```powershell
# Allow script execution (run as Administrator)
Set-ExecutionPolicy RemoteSigned -Scope CurrentUser

# Then run the script
.\make.ps1 install
```

**Problem: Python not found**

Solution:
```cmd
REM Ensure Python is in PATH
python --version

REM If not, use full path or add to PATH
REM Edit make.bat and set:
REM set PYTHON=C:\Python310\python.exe
```

## Advanced Usage

### Custom Configuration Path

**Linux/macOS:**
```bash
# Edit Makefile and add custom config path
# Or export environment variable
export CONFIG_PATH=/path/to/custom/devices.yaml
make discover
```

### Production Deployment

**Linux/macOS:**
```bash
# Install for production
make prod-install

# Start production server with Gunicorn
make prod-serve
```

### Database Management

**Linux/macOS:**
```bash
# Backup before major changes
make db-backup

# View database
make db-shell

# Initialize fresh database
make db-clean
make db-init
```

### Scheduled Discovery

**Linux (cron):**
```bash
# Edit crontab
crontab -e

# Add daily discovery at 2 AM
0 2 * * * cd /path/to/project && make discover >> /var/log/network-discovery.log 2>&1
```

**Windows (Task Scheduler):**
```cmd
REM Create scheduled task
schtasks /create /tn "Network Discovery" /tr "C:\path\to\project\make.bat discover" /sc daily /st 02:00
```

## Platform-Specific Features

### Linux/macOS Only (Makefile)

- **Colored output** - Automatic colored terminal output
- **Pattern rules** - Advanced make features
- **Shell integration** - Better shell command handling
- **Parallel execution** - Can run multiple targets in parallel

### Windows Only (make.bat / make.ps1)

- **PowerShell version** - `make.ps1` has better error handling and colored output
- **CMD version** - `make.bat` works everywhere but has basic features
- **Native Windows paths** - Handles backslashes correctly

## Tips

1. **Use tab completion** (Linux/macOS):
   ```bash
   make <tab><tab>  # Shows available targets
   ```

2. **View command before running**:
   ```bash
   make -n discover  # Dry run (Linux/macOS)
   ```

3. **Run multiple commands**:
   ```bash
   make install discover serve  # Linux/macOS
   ```
   ```cmd
   make.bat install && make.bat discover && make.bat serve  # Windows
   ```

4. **Create aliases** (Linux/macOS):
   ```bash
   # Add to ~/.bashrc or ~/.zshrc
   alias nd='make'
   alias nd-discover='make discover'
   alias nd-serve='make serve'
   ```

5. **Create shortcuts** (Windows):
   ```cmd
   REM Create batch file: nd.bat
   @echo off
   make.bat %*

   REM Then use:
   nd discover
   nd serve
   ```

## Summary

The makefiles provide a unified interface for all project operations:

- ✅ **Cross-platform** - Works on Linux, macOS, and Windows
- ✅ **Easy to use** - Simple command syntax
- ✅ **Complete** - Covers all project operations
- ✅ **Documented** - Built-in help with `make help`
- ✅ **Consistent** - Same commands across platforms

Choose the right version for your platform:
- **Linux/macOS**: Use `Makefile` with `make`
- **Windows (cmd)**: Use `make.bat`
- **Windows (PowerShell)**: Use `make.ps1` for better experience

## Getting Help

1. Show all commands:
   ```bash
   make help              # Linux/macOS
   make.bat help          # Windows cmd
   .\make.ps1 help        # Windows PowerShell
   ```

2. Check documentation:
   - `README.md` - Project overview
   - `INSTALLATION.md` - Installation guide
   - `USAGE.md` - Detailed usage
   - `MAKEFILE_GUIDE.md` - This file

3. Open an issue on GitHub for problems or questions
