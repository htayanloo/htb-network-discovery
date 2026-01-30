# Network Discovery and Visualization Tool

A Python-based Cisco network discovery application that connects via SSH, discovers topology using CDP/LLDP, and provides interactive visualization with MAC address search capabilities.

![Python Version](https://img.shields.io/badge/python-3.10%2B-blue)
![License](https://img.shields.io/badge/license-MIT-green)

## Features

- 🔍 **Automated Network Discovery**: Recursively discovers Cisco switches via CDP/LLDP
- 🌐 **Interactive Visualization**: Web-based network diagram using Cytoscape.js
- 🔎 **MAC Address Search**: Find where any MAC address appears in your network
- 📊 **Interface Information**: Detailed interface status, speed, VLAN, and trunk information
- 🗄️ **Data Persistence**: SQLite database for historical tracking
- 🖥️ **CLI and Web Interface**: Use command-line tools or web dashboard
- 📤 **Export Capabilities**: Export topology to JSON, GraphML, or GEXF formats
- 🔀 **Topology Analysis**: Path finding, loop detection, and network statistics

## Quick Start

### Using Makefile (Recommended)

**Linux/macOS:**
```bash
make install          # Install everything
make discover         # Run discovery
make serve           # Start web dashboard
```

**Windows (Command Prompt):**
```cmd
make.bat install     # Install everything
make.bat discover    # Run discovery
make.bat serve      # Start web dashboard
```

**Windows (PowerShell):**
```powershell
.\make.ps1 install   # Install everything
.\make.ps1 discover  # Run discovery
.\make.ps1 serve    # Start web dashboard
```

See [MAKEFILE_GUIDE.md](MAKEFILE_GUIDE.md) for complete makefile documentation.

### Manual Installation

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
pip install -e .

# Configure
cp config/devices.yaml.example config/devices.yaml
# Edit config/devices.yaml with your network details

# Set SSH password
export SSH_PASSWORD="your-password"  # Linux/macOS
set SSH_PASSWORD=your-password       # Windows cmd
$env:SSH_PASSWORD="your-password"    # Windows PowerShell

# Run discovery
network-discovery discover run

# Start web dashboard
network-discovery serve
# Then open web/index.html in browser
```

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         User Interfaces                         │
├──────────────────────────┬──────────────────────────────────────┤
│   CLI Tool (Typer)       │   Web Dashboard (Cytoscape.js)       │
└──────────────┬───────────┴────────────────┬─────────────────────┘
               │                            │
               └────────────┬───────────────┘
                            │
                ┌───────────▼────────────┐
                │   Core Service Layer   │
                │  - Discovery Engine    │
                │  - Topology Builder    │
                └───────────┬────────────┘
                            │
           ┌────────────────┼────────────────┐
           │                │                │
    ┌──────▼──────┐  ┌─────▼─────┐  ┌──────▼──────┐
    │  SSH Client │  │  Database │  │  Exporters  │
    │  (Netmiko)  │  │  (SQLite) │  │ (JSON/GML)  │
    └──────┬──────┘  └───────────┘  └─────────────┘
           │
    ┌──────▼──────────┐
    │ Cisco Switches  │
    └─────────────────┘
```

## Technology Stack

- **Language**: Python 3.10+
- **SSH Library**: Netmiko (robust CLI interaction)
- **Graph Processing**: NetworkX (topology analysis)
- **Database**: SQLite with SQLAlchemy ORM
- **Web Framework**: Flask + Flask-CORS
- **CLI Framework**: Typer (modern, type-hinted CLI)
- **Visualization**: Cytoscape.js (network visualization)
- **API**: RESTful JSON API

## CLI Commands

### Discovery
```bash
network-discovery discover run                    # Run discovery
network-discovery discover run --max-depth 5      # Limit depth
network-discovery discover status                 # Show last session
```

### Search
```bash
network-discovery search mac aa:bb:cc:dd:ee:ff    # Find MAC address
network-discovery search device SWITCH-01         # Find device
```

### List
```bash
network-discovery list-devices                    # List all devices
network-discovery list-devices --type switch      # List switches only
network-discovery list-connections                # List connections
```

### Export
```bash
network-discovery export --format json --output topology.json
network-discovery export --format graphml --output topology.graphml
```

### Web Dashboard
```bash
network-discovery serve                           # Start server
network-discovery serve --port 8080               # Custom port
network-discovery serve --debug                   # Debug mode
```

### Statistics
```bash
network-discovery stats                           # Show topology statistics
```

### Makefile Commands (Easier!)

Instead of remembering all CLI commands, use the Makefile:

```bash
# Linux/macOS
make help                  # Show all commands
make discover             # Run discovery
make search-mac MAC=aa:bb:cc:dd:ee:ff
make export-all           # Export all formats
make serve               # Start server

# Windows
make.bat help            # Show all commands
make.bat discover        # Run discovery
make.bat serve          # Start server
```

## REST API

The Flask API provides endpoints for programmatic access:

- `GET /api/topology` - Full network topology
- `GET /api/devices` - List all devices
- `GET /api/devices/<id>` - Device details
- `GET /api/search/mac/<mac>` - Search MAC address
- `GET /api/search/device?q=<query>` - Search devices
- `GET /api/topology/stats` - Topology statistics
- `GET /api/topology/path?source=SW1&target=SW2` - Find path

See [USAGE.md](USAGE.md) for complete API documentation.

## Web Dashboard

The web dashboard provides:

- **Interactive Topology View**: Zoom, pan, explore
- **Device Details**: Click nodes for information
- **MAC Search**: Find MAC addresses instantly
- **Device Search**: Locate devices by hostname/IP
- **Multiple Layouts**: Force-directed, circle, grid, hierarchical
- **Export**: Download topology as JSON

## Configuration

Edit `config/devices.yaml`:

```yaml
seed_devices:
  - hostname: CORE-SW-01
    ip: 192.168.1.1
    device_type: cisco_ios

credentials:
  username: admin
  # Password from environment variable

discovery_options:
  recursive: true
  max_depth: 10
  timeout: 30
  collect_mac_tables: true
  protocols:
    - cdp
    - lldp

parallel:
  max_workers: 5
```

## Project Structure

```
htb-network-discovery/
├── src/                    # Python source code
│   ├── cli/               # CLI commands
│   ├── core/              # Discovery & topology logic
│   ├── database/          # Database models & repositories
│   ├── api/               # Flask REST API
│   └── utils/             # Config, logging, validators
├── web/                    # Web dashboard (HTML/CSS/JS)
├── config/                 # Configuration files
├── tests/                  # Test suite
├── Makefile               # Linux/macOS automation
├── make.bat               # Windows batch automation
├── make.ps1               # Windows PowerShell automation
└── requirements.txt        # Python dependencies
```

## Documentation

- **[INSTALLATION.md](INSTALLATION.md)** - Detailed installation guide
- **[USAGE.md](USAGE.md)** - Comprehensive usage guide
- **[MAKEFILE_GUIDE.md](MAKEFILE_GUIDE.md)** - Makefile commands reference
- **[IMPLEMENTATION_SUMMARY.md](IMPLEMENTATION_SUMMARY.md)** - Technical implementation details

## Examples

### Example 1: Basic Discovery

```bash
# Using Makefile (easiest)
make install
make discover
make list-devices

# Or using CLI directly
network-discovery discover run
network-discovery list-devices
network-discovery stats
```

### Example 2: Search Operations

```bash
# Search for MAC address
make search-mac MAC=00:50:56:12:34:56

# Search for device
make search-device DEVICE=CORE-SW-01
```

### Example 3: Export and Analysis

```bash
# Export topology
make export-json
make export-graphml

# View statistics
make stats

# Start web dashboard
make serve
```

## Troubleshooting

### SSH Connection Issues
- Verify network connectivity: `ping <device-ip>`
- Check credentials and SSH access
- Ensure SSH is enabled on devices: `show ip ssh`
- Increase timeout in `config/devices.yaml`

### Discovery Not Finding Neighbors
- Verify CDP/LLDP is enabled: `show cdp neighbors`
- Check device types in configuration
- Review logs in `logs/discovery.log`

### Web Dashboard Not Loading
- Ensure API server is running: `make serve`
- Check browser console for errors
- Verify API URL in `web/app.js`

## Performance

The tool is optimized for:

- **Parallel Discovery**: Up to 15 concurrent SSH connections
- **Efficient Parsing**: Regex-based parsers for fast processing
- **Indexed Database**: Fast MAC address lookups
- **Client-side Rendering**: Smooth web UI with Cytoscape.js

**Benchmark Estimates:**
- Small Network (10 devices): ~1-2 minutes
- Medium Network (50 devices): ~5-10 minutes
- Large Network (100+ devices): ~15-30 minutes

## Security

- ✅ Credentials stored in environment variables
- ✅ SSH key support
- ✅ Input validation on all inputs
- ✅ Read-only device access (no configuration changes)
- ✅ CORS configuration for API

## Contributing

Contributions welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Submit a pull request

## License

MIT License

## Support

For issues and questions:
- Check logs in `logs/discovery.log`
- Review documentation files
- Open an issue on GitHub

## Acknowledgments

- Built with Python, Flask, NetworkX, and Cytoscape.js
- Uses Netmiko for SSH connections
- Inspired by network discovery tools

---

**Made with ❤️ for network engineers**
