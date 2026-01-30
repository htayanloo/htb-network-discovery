# Installation Guide

## Prerequisites

- Python 3.10 or higher
- SSH access to Cisco network devices
- Network connectivity to target devices
- Bash shell (Linux/macOS) or PowerShell (Windows)

## Step 1: Clone or Download Project

```bash
cd /path/to/projects
# If you have the project already:
cd htb-network-discovery
```

## Step 2: Create Virtual Environment

### Linux/macOS

```bash
python3 -m venv venv
source venv/bin/activate
```

### Windows

```bash
python -m venv venv
venv\Scripts\activate
```

## Step 3: Install Dependencies

```bash
# Upgrade pip
pip install --upgrade pip

# Install requirements
pip install -r requirements.txt

# Install package in development mode
pip install -e .
```

## Step 4: Configure Application

### Create Configuration File

```bash
# Copy example configuration
cp config/devices.yaml.example config/devices.yaml

# Edit with your network details
nano config/devices.yaml
# or
vim config/devices.yaml
```

### Configure Environment Variables

```bash
# Copy environment template
cp .env.example .env

# Edit environment file
nano .env
```

Add your SSH credentials:

```bash
# SSH Configuration
SSH_USERNAME=admin
SSH_PASSWORD=your-password-here

# Or use SSH keys (recommended)
# Leave SSH_PASSWORD empty and configure key_file in devices.yaml
```

### Example Configuration

Edit `config/devices.yaml`:

```yaml
seed_devices:
  - hostname: CORE-SW-01
    ip: 192.168.1.1
    device_type: cisco_ios

  - hostname: DIST-SW-01
    ip: 192.168.1.2
    device_type: cisco_ios

credentials:
  username: admin
  # Password from environment variable

discovery_options:
  recursive: true
  max_depth: 10
  timeout: 30
  collect_mac_tables: true
```

## Step 5: Verify Installation

```bash
# Check if command is available
network-discovery --help

# Should show:
# Usage: network-discovery [OPTIONS] COMMAND [ARGS]...
#
# Network Discovery and Visualization Tool
```

## Step 6: Test SSH Connection

Before running full discovery, test SSH connection:

```bash
# Using netmiko directly
python <<EOF
from netmiko import ConnectHandler

device = {
    'device_type': 'cisco_ios',
    'host': '192.168.1.1',
    'username': 'admin',
    'password': 'your-password',
}

try:
    connection = ConnectHandler(**device)
    output = connection.send_command('show version')
    print("✓ Connection successful!")
    print(output[:200])  # First 200 chars
    connection.disconnect()
except Exception as e:
    print(f"✗ Connection failed: {e}")
EOF
```

## Step 7: Run First Discovery

```bash
# Run discovery
network-discovery discover run

# This will:
# 1. Connect to seed devices
# 2. Collect device information
# 3. Discover neighbors via CDP/LLDP
# 4. Store data in SQLite database
# 5. Display summary
```

## Step 8: Start Web Dashboard

```bash
# Start API server
network-discovery serve
```

Then open `web/index.html` in your browser.

## Troubleshooting Installation

### Problem: `command not found: network-discovery`

**Solution**:
```bash
# Ensure virtual environment is activated
source venv/bin/activate  # Linux/macOS
venv\Scripts\activate     # Windows

# Reinstall package
pip install -e .
```

### Problem: `ModuleNotFoundError: No module named 'netmiko'`

**Solution**:
```bash
# Install requirements again
pip install -r requirements.txt
```

### Problem: SSH Connection Timeout

**Solution**:
- Check network connectivity: `ping <device-ip>`
- Verify SSH is enabled on device: `show ip ssh`
- Increase timeout in `config/devices.yaml`:
  ```yaml
  discovery_options:
    timeout: 60
    banner_timeout: 30
  ```

### Problem: Authentication Failed

**Solution**:
- Verify credentials are correct
- Check if environment variable is set:
  ```bash
  echo $SSH_PASSWORD
  ```
- Try using SSH keys instead:
  ```yaml
  credentials:
    username: admin
    use_keys: true
    key_file: ~/.ssh/id_rsa
  ```

### Problem: Permission Denied on Cisco Device

**Solution**:
- Ensure user has privilege level 15 or enable password configured
- Add enable password to configuration:
  ```yaml
  seed_devices:
    - hostname: SWITCH-01
      ip: 192.168.1.1
      secret: enable-password-here
  ```

## Directory Structure After Installation

```
htb-network-discovery/
├── venv/                    # Virtual environment (created)
├── src/                     # Source code
├── config/
│   ├── devices.yaml         # Your configuration (created)
│   └── devices.yaml.example # Template
├── logs/                    # Log files (created on first run)
├── web/                     # Web dashboard
├── network_discovery.db     # Database (created on first discovery)
├── requirements.txt
├── setup.py
└── README.md
```

## Next Steps

1. ✓ Installation complete
2. ✓ Configuration set up
3. ✓ First discovery run
4. → Explore web dashboard
5. → Schedule regular discoveries
6. → Integrate with monitoring tools

## Uninstallation

To remove the application:

```bash
# Deactivate virtual environment
deactivate

# Remove virtual environment
rm -rf venv/

# Remove database and logs (optional)
rm -f network_discovery.db
rm -rf logs/

# The source code remains for future use
```

## Updating

To update to a new version:

```bash
# Activate virtual environment
source venv/bin/activate

# Pull latest changes (if using git)
git pull

# Update dependencies
pip install --upgrade -r requirements.txt

# Reinstall package
pip install -e .
```

## Production Deployment

For production use:

1. **Use PostgreSQL instead of SQLite**:
   ```bash
   export DATABASE_URL="postgresql://user:pass@localhost/netdiscovery"
   ```

2. **Run as a service** (systemd on Linux):
   ```ini
   [Unit]
   Description=Network Discovery Service
   After=network.target

   [Service]
   Type=simple
   User=netdiscovery
   WorkingDirectory=/opt/network-discovery
   ExecStart=/opt/network-discovery/venv/bin/network-discovery serve
   Restart=always

   [Install]
   WantedBy=multi-user.target
   ```

3. **Use Gunicorn for API**:
   ```bash
   pip install gunicorn
   gunicorn -w 4 -b 0.0.0.0:5000 api.app:create_app()
   ```

4. **Set up reverse proxy** (nginx):
   ```nginx
   server {
       listen 80;
       server_name netdiscovery.example.com;

       location /api {
           proxy_pass http://localhost:5000;
       }

       location / {
           root /opt/network-discovery/web;
           index index.html;
       }
   }
   ```

## Support

If you encounter issues:

1. Check logs: `tail -f logs/discovery.log`
2. Review error messages
3. Consult USAGE.md for detailed commands
4. Open an issue on GitHub

## Security Notes

- Never commit `config/devices.yaml` with credentials
- Use SSH keys instead of passwords when possible
- Restrict API access in production
- Regularly rotate credentials
- Run discovery from secure management network
