# Quick Start Guide

Get up and running in 5 minutes!

## Prerequisites

- Python 3.10 or higher
- SSH access to Cisco devices
- Network connectivity

## Installation (Choose Your Platform)

### Linux/macOS

```bash
# One-line install
make install
```

### Windows (Command Prompt)

```cmd
REM One-line install
make.bat install
```

### Windows (PowerShell)

```powershell
# One-line install
.\make.ps1 install
```

## Configuration

1. **Edit device configuration:**

   ```bash
   # Linux/macOS
   nano config/devices.yaml

   # Windows
   notepad config\devices.yaml
   ```

2. **Add your seed devices:**

   ```yaml
   seed_devices:
     - hostname: CORE-SW-01
       ip: 192.168.1.1
       device_type: cisco_ios

   credentials:
     username: admin
   ```

3. **Set SSH password:**

   ```bash
   # Linux/macOS
   export SSH_PASSWORD="your-password"

   # Windows (cmd)
   set SSH_PASSWORD=your-password

   # Windows (PowerShell)
   $env:SSH_PASSWORD = "your-password"
   ```

## Run Discovery

### Linux/macOS

```bash
make discover
```

### Windows

```cmd
make.bat discover
```

## View Results

### Linux/macOS

```bash
# List devices
make list-devices

# Show statistics
make stats

# Start web dashboard
make serve
```

### Windows

```cmd
REM List devices
make.bat list-devices

REM Show statistics
make.bat stats

REM Start web dashboard
make.bat serve
```

Then open `web/index.html` in your browser.

## Common Tasks

### Search for MAC Address

**Linux/macOS:**
```bash
make search-mac MAC=aa:bb:cc:dd:ee:ff
```

**Windows (cmd):**
```cmd
set MAC=aa:bb:cc:dd:ee:ff
make.bat search-mac
```

**Windows (PowerShell):**
```powershell
.\make.ps1 search-mac aa:bb:cc:dd:ee:ff
```

### Search for Device

**Linux/macOS:**
```bash
make search-device DEVICE=SWITCH-01
```

**Windows (cmd):**
```cmd
set DEVICE=SWITCH-01
make.bat search-device
```

**Windows (PowerShell):**
```powershell
.\make.ps1 search-device SWITCH-01
```

### Export Topology

**Linux/macOS:**
```bash
make export-all
```

**Windows:**
```cmd
make.bat export-all
```

## Complete Workflow

### Linux/macOS

```bash
# 1. Install
make install

# 2. Edit config
nano config/devices.yaml

# 3. Set password
export SSH_PASSWORD="password"

# 4. Discover
make discover

# 5. View results
make list-devices
make stats

# 6. Search
make search-mac MAC=00:11:22:33:44:55

# 7. Export
make export-all

# 8. Web dashboard
make serve
# Open web/index.html
```

### Windows (Command Prompt)

```cmd
REM 1. Install
make.bat install

REM 2. Edit config
notepad config\devices.yaml

REM 3. Set password
set SSH_PASSWORD=password

REM 4. Discover
make.bat discover

REM 5. View results
make.bat list-devices
make.bat stats

REM 6. Search
set MAC=00:11:22:33:44:55
make.bat search-mac

REM 7. Export
make.bat export-all

REM 8. Web dashboard
make.bat serve
REM Open web\index.html
```

### Windows (PowerShell)

```powershell
# 1. Install
.\make.ps1 install

# 2. Edit config
notepad config\devices.yaml

# 3. Set password
$env:SSH_PASSWORD = "password"

# 4. Discover
.\make.ps1 discover

# 5. View results
.\make.ps1 list-devices
.\make.ps1 stats

# 6. Search
.\make.ps1 search-mac 00:11:22:33:44:55

# 7. Export
.\make.ps1 export-all

# 8. Web dashboard
.\make.ps1 serve
# Open web\index.html
```

## Troubleshooting

### Can't connect to devices?

1. Test connectivity: `ping 192.168.1.1`
2. Verify SSH is enabled on device
3. Check credentials
4. Increase timeout in `config/devices.yaml`:
   ```yaml
   discovery_options:
     timeout: 60
   ```

### Discovery finds no neighbors?

1. Check CDP/LLDP is enabled:
   ```
   show cdp neighbors
   show lldp neighbors
   ```
2. Review logs: `tail -f logs/discovery.log`

### Web dashboard won't load?

1. Make sure server is running: `make serve`
2. Check browser console for errors
3. Verify API is accessible: `curl http://localhost:5000/api/topology`

## Help

### Show all commands

**Linux/macOS:**
```bash
make help
```

**Windows:**
```cmd
make.bat help
```

**PowerShell:**
```powershell
.\make.ps1 help
```

### Read documentation

- [README.md](README.md) - Project overview
- [INSTALLATION.md](INSTALLATION.md) - Detailed installation
- [USAGE.md](USAGE.md) - Complete usage guide
- [MAKEFILE_GUIDE.md](MAKEFILE_GUIDE.md) - Makefile reference

## Next Steps

1. ✅ Installation complete
2. ✅ First discovery done
3. ✅ Explored web dashboard
4. → Schedule regular discoveries
5. → Export data for analysis
6. → Integrate with monitoring tools

## Support

- Check logs: `logs/discovery.log`
- Open an issue on GitHub
- Read the documentation files

---

**You're all set! Happy discovering! 🚀**
