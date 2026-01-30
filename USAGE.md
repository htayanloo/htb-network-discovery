# Network Discovery Tool - Usage Guide

## Quick Start

### 1. Installation

```bash
# Navigate to project directory
cd htb-network-discovery

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Install package in development mode
pip install -e .
```

### 2. Configuration

```bash
# Copy configuration template
cp config/devices.yaml.example config/devices.yaml

# Edit configuration
nano config/devices.yaml
```

Configure your seed devices:

```yaml
seed_devices:
  - hostname: CORE-SW-01
    ip: 192.168.1.1
    device_type: cisco_ios

credentials:
  username: admin
```

Set SSH password as environment variable:

```bash
export SSH_PASSWORD="your-password"
```

### 3. Run Discovery

```bash
# Run network discovery
network-discovery discover run

# Or with custom configuration
network-discovery discover run --config config/devices.yaml --max-depth 5
```

## CLI Commands

### Discovery Commands

```bash
# Run discovery
network-discovery discover run

# Check last discovery status
network-discovery discover status
```

### List Commands

```bash
# List all devices
network-discovery list-devices

# List switches only
network-discovery list-devices --type switch

# List all connections
network-discovery list-connections
```

### Search Commands

```bash
# Search for MAC address
network-discovery search mac aa:bb:cc:dd:ee:ff

# Search for device
network-discovery search device SWITCH-01
network-discovery search device 192.168.1.1
```

### Export Commands

```bash
# Export topology as JSON
network-discovery export --format json --output topology.json
network-discovery export --format json  # Outputs to console

# Export as GraphML (for Gephi, yEd)
network-discovery export --format graphml --output topology.graphml

# Export as GEXF
network-discovery export --format gexf --output topology.gexf
```

### Statistics

```bash
# Show topology statistics
network-discovery stats
```

### Web Dashboard

```bash
# Start web dashboard server
network-discovery serve

# Custom host and port
network-discovery serve --host 0.0.0.0 --port 8080

# With debug mode
network-discovery serve --debug
```

Then open `web/index.html` in your browser.

## API Endpoints

The REST API is available at `http://localhost:5000/api` when running the server.

### Topology Endpoints

- `GET /api/topology` - Get full network topology
- `GET /api/topology/stats` - Get topology statistics
- `GET /api/topology/path?source=SW1&target=SW2` - Find path between devices
- `GET /api/topology/neighbors/<device>` - Get device neighbors
- `GET /api/topology/analysis` - Analyze topology

### Device Endpoints

- `GET /api/devices` - List all devices
- `GET /api/devices?type=switch` - Filter by type
- `GET /api/devices/<id>` - Get device details
- `GET /api/devices/<id>/interfaces` - Get device interfaces
- `GET /api/devices/<id>/vlans` - Get device VLANs
- `GET /api/devices/hostname/<hostname>` - Get device by hostname
- `GET /api/vlans` - List all VLANs

### Search Endpoints

- `GET /api/search/mac/<mac_address>` - Search for MAC address
- `GET /api/search/device?q=<query>` - Search devices
- `GET /api/search/interface?q=<query>` - Search interfaces

## Web Dashboard Usage

### Features

1. **Interactive Topology View**
   - Zoom, pan, and explore network diagram
   - Click nodes to see device details
   - Different layouts available (force-directed, circle, grid, hierarchical)

2. **Search Functionality**
   - Search for MAC addresses
   - Search for devices by hostname or IP
   - Results highlighted on diagram

3. **Device Details**
   - Click any device to see:
     - Hostname and IP
     - Model and IOS version
     - Interface count
     - Neighbors

4. **Export**
   - Export topology as JSON
   - Download for offline analysis

### Controls

- **Fit**: Fit entire topology to screen
- **Refresh**: Reload topology from API
- **Export JSON**: Download topology data
- **Layout dropdown**: Change visualization layout

## Configuration Options

### Discovery Options

```yaml
discovery_options:
  recursive: true          # Discover neighbors recursively
  max_depth: 10           # Maximum recursion depth
  timeout: 30             # SSH timeout (seconds)
  banner_timeout: 15      # Banner timeout (seconds)
  collect_mac_tables: true    # Collect MAC address tables
  collect_arp_tables: false   # Collect ARP tables
  collect_interface_stats: true  # Collect interface statistics
  protocols:
    - cdp                 # Use CDP
    - lldp                # Use LLDP
```

### Parallel Processing

```yaml
parallel:
  max_workers: 5          # Number of concurrent SSH connections
  queue_size: 100         # Discovery queue size
```

### Filters

```yaml
filters:
  exclude_hostnames:      # Skip devices matching these patterns
    - "*-AP-*"           # Skip access points
    - "*-PHONE-*"        # Skip IP phones
```

## Database

The tool uses SQLite by default. Database file: `network_discovery.db`

To use a different database, set the `DATABASE_URL` environment variable:

```bash
export DATABASE_URL="postgresql://user:pass@localhost/netdiscovery"
```

## Troubleshooting

### SSH Connection Issues

**Problem**: Cannot connect to devices

**Solutions**:
- Verify network connectivity: `ping <device-ip>`
- Check SSH credentials
- Ensure SSH is enabled on devices: `show ip ssh`
- Check firewall rules

### Discovery Not Finding Neighbors

**Problem**: Discovery only finds seed devices

**Solutions**:
- Verify CDP/LLDP is enabled: `show cdp neighbors`
- Check device types in configuration
- Review discovery logs in `logs/discovery.log`
- Increase max_depth if needed

### Web Dashboard Not Loading

**Problem**: Dashboard shows "Failed to load topology"

**Solutions**:
- Ensure API server is running: `network-discovery serve`
- Check API URL in `web/app.js` (default: `http://localhost:5000`)
- Verify CORS settings
- Check browser console for errors

### Missing MAC Addresses

**Problem**: MAC addresses not being recorded

**Solutions**:
- Ensure `collect_mac_tables: true` in configuration
- Verify device has `show mac address-table` command
- Check database for entries: `network-discovery search mac <mac>`

## Performance Tips

1. **Large Networks** (100+ devices)
   - Increase `max_workers` to 10-15
   - Use `collect_mac_tables: false` for faster discovery
   - Consider running discovery during off-hours

2. **Slow Devices**
   - Increase `timeout` to 60 seconds
   - Use `banner_timeout: 30`
   - Disable interface statistics collection

3. **Frequent Discovery**
   - Use database to avoid full rediscovery
   - Only re-scan changed devices
   - Schedule discoveries with cron

## Advanced Usage

### Custom Parsers

To support additional Cisco command outputs, extend `src/core/discovery/parsers.py`:

```python
@staticmethod
def parse_custom_command(output: str) -> List[Dict[str, Any]]:
    # Your parsing logic
    pass
```

### Custom Device Types

To support non-Cisco devices, create a new collector in `src/core/discovery/collectors.py`.

### API Integration

Use the REST API to integrate with other tools:

```python
import requests

# Get topology
response = requests.get('http://localhost:5000/api/topology')
topology = response.json()

# Search MAC
response = requests.get('http://localhost:5000/api/search/mac/aa:bb:cc:dd:ee:ff')
result = response.json()
```

## Security Best Practices

1. **Credentials**
   - Use SSH keys instead of passwords
   - Store passwords in environment variables
   - Never commit credentials to version control

2. **Network Access**
   - Run discovery from management network
   - Use read-only SNMP credentials if applicable
   - Implement access controls on API

3. **Data Protection**
   - Encrypt database if it contains sensitive information
   - Regularly rotate credentials
   - Audit discovery logs

## Examples

### Example 1: Basic Discovery

```bash
# Configure seed devices
cat > config/devices.yaml <<EOF
seed_devices:
  - hostname: CORE-SW-01
    ip: 10.0.0.1
    device_type: cisco_ios

credentials:
  username: netadmin
EOF

# Set password
export SSH_PASSWORD="MySecureP@ssw0rd"

# Run discovery
network-discovery discover run

# View results
network-discovery list-devices
network-discovery stats
```

### Example 2: Search and Export

```bash
# Search for a MAC address
network-discovery search mac 00:50:56:12:34:56

# Search for a device
network-discovery search device DIST-SW-01

# Export topology
network-discovery export --format json --output /tmp/topology.json

# Start web dashboard
network-discovery serve --port 8080
```

### Example 3: Scheduled Discovery

Create a cron job:

```bash
# Edit crontab
crontab -e

# Add discovery job (runs daily at 2 AM)
0 2 * * * cd /path/to/htb-network-discovery && /path/to/venv/bin/network-discovery discover run >> /var/log/network-discovery.log 2>&1
```

## Support

For issues and questions:
- Check logs in `logs/discovery.log`
- Review error messages in CLI output
- Open an issue on GitHub
- Consult the README.md for architecture details

## Next Steps

1. Run your first discovery
2. Explore the web dashboard
3. Integrate with your monitoring tools
4. Schedule regular discoveries
5. Analyze topology changes over time
