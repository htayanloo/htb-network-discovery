# UV Package Manager Guide

## What is UV?

UV is an **ultra-fast Python package installer and resolver** written in Rust. It's a drop-in replacement for pip and pip-tools that's 10-100x faster than traditional Python package managers.

### Key Benefits

✨ **10-100x Faster** - UV is written in Rust and optimized for speed
🔒 **Better Dependency Resolution** - More accurate than pip
🎯 **Drop-in Replacement** - Works with existing `requirements.txt` files
💾 **Smaller Disk Usage** - Efficient caching and storage
🚀 **Modern Tool** - Built by the creators of Ruff (the fast Python linter)

## Installation

UV is automatically installed when you run `make install` on any platform.

### Manual Installation

**Linux/macOS:**
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

**Windows (PowerShell):**
```powershell
irm https://astral.sh/uv/install.ps1 | iex
```

**Using Makefile:**
```bash
make install-uv          # Linux/macOS
make.bat install-uv      # Windows cmd
.\make.ps1 install-uv    # Windows PowerShell
```

## How UV is Used in This Project

All Makefiles have been updated to use UV for:

1. **Creating Virtual Environments**
   ```bash
   uv venv .venv
   ```
   Instead of: `python -m venv venv`

2. **Installing Dependencies**
   ```bash
   uv pip install -r requirements.txt
   ```
   Instead of: `pip install -r requirements.txt`

3. **Running Commands**
   ```bash
   uv run network-discovery discover run
   ```
   Instead of: `.venv/bin/network-discovery discover run`

## Commands with UV

### Setup Commands

```bash
# Install UV
make install-uv

# Create virtual environment with UV
make venv

# Install dependencies (ultra-fast!)
make deps

# Sync dependencies (even faster than install)
make sync
```

### Running Commands

UV automatically activates the virtual environment when using `uv run`:

```bash
# Traditional way (requires activation)
source .venv/bin/activate
network-discovery discover run

# UV way (no activation needed!)
uv run network-discovery discover run

# Or use the Makefile (uses UV internally)
make discover
```

### Benefits in This Project

#### Speed Comparison

**Installing 40+ packages:**
- **Traditional pip**: ~30-60 seconds
- **UV**: ~3-5 seconds ⚡

**Creating virtual environment:**
- **venv**: ~2-3 seconds
- **UV**: ~0.5 seconds ⚡

#### Disk Usage

UV uses a global cache, so:
- Multiple projects share dependencies
- Less disk space used
- Faster subsequent installs

## UV Commands Used

### Package Management

```bash
# Install packages
uv pip install <package>

# Install from requirements
uv pip install -r requirements.txt

# Sync to requirements (removes extras)
uv pip sync requirements.txt

# Upgrade all packages
uv pip install --upgrade -r requirements.txt

# Freeze dependencies
uv pip freeze > requirements.lock

# Check for issues
uv pip check

# List installed packages
uv pip list
```

### Virtual Environment

```bash
# Create virtual environment
uv venv .venv

# Create with specific Python version
uv venv --python 3.11 .venv

# Remove virtual environment
rm -rf .venv
```

### Running Commands

```bash
# Run command in virtual environment
uv run <command>

# Run Python script
uv run python script.py

# Run installed tool
uv run network-discovery discover run
```

## Makefile Integration

All three Makefiles use UV:

### Linux/macOS (Makefile)

```makefile
UV := uv
UV_RUN := $(UV) run

venv:
	@$(UV) venv .venv

deps:
	@$(UV) pip install -r requirements.txt

discover:
	@$(UV_RUN) network-discovery discover run
```

### Windows (make.bat & make.ps1)

```batch
set UV=uv
set UV_RUN=%UV% run

%UV% venv .venv
%UV% pip install -r requirements.txt
%UV_RUN% network-discovery discover run
```

## Comparison: pip vs UV

| Feature | pip | UV |
|---------|-----|-----|
| **Speed** | Baseline | 10-100x faster |
| **Dependency Resolution** | Basic | Advanced |
| **Caching** | Per-project | Global cache |
| **Disk Usage** | Higher | Lower |
| **Language** | Python | Rust |
| **Compatibility** | 100% | 100% (drop-in replacement) |

## Common Workflows

### First-Time Setup

```bash
# Install UV
make install-uv

# Create venv and install everything
make install

# Done! UV handled everything fast.
```

### Daily Development

```bash
# Activate venv (optional with UV)
source .venv/bin/activate  # Linux/macOS
.venv\Scripts\activate     # Windows

# Or just use UV run
uv run network-discovery discover run

# Or use Makefile (easiest)
make discover
```

### Adding New Packages

```bash
# Add to requirements.txt
echo "new-package==1.0.0" >> requirements.txt

# Install with UV (fast!)
make deps

# Or directly
uv pip install new-package
```

### Updating Dependencies

```bash
# Update all packages
make update-deps

# Or with UV directly
uv pip install --upgrade -r requirements.txt
```

## Troubleshooting

### UV Not Found

```bash
# Check if UV is installed
uv --version

# If not, install it
make install-uv
```

### UV Command Fails

```bash
# Ensure you're in the project directory
cd /path/to/htb-network-discovery

# Verify virtual environment exists
ls .venv

# If not, create it
make venv
```

### Packages Not Found

```bash
# Sync dependencies
uv pip sync requirements.txt

# Or reinstall
make clean
make install
```

### Permission Issues (Linux/macOS)

```bash
# UV installs to ~/.cargo/bin
# Ensure it's in PATH
echo 'export PATH="$HOME/.cargo/bin:$PATH"' >> ~/.bashrc
source ~/.bashrc
```

## Advanced Features

### Python Version Management

UV can work with different Python versions:

```bash
# Create venv with specific Python
uv venv --python 3.11 .venv
uv venv --python 3.12 .venv

# UV will download Python if needed
```

### Dependency Compilation

For projects with `pyproject.toml`:

```bash
# Compile dependencies
uv pip compile pyproject.toml -o requirements.txt
```

### Lock Files

Create reproducible builds:

```bash
# Create lock file
make freeze

# This creates requirements.lock with exact versions
uv pip install -r requirements.lock
```

## Migration from pip

Migrating to UV is seamless:

1. ✅ All existing `requirements.txt` files work
2. ✅ Virtual environments are compatible
3. ✅ Commands are the same (`uv pip` instead of `pip`)
4. ✅ No code changes needed

## Performance Tips

1. **Use `uv pip sync`** for faster reinstalls (removes unneeded packages)
2. **Keep UV updated** - `uv self update` (on systems that support it)
3. **Use global cache** - UV automatically caches downloads
4. **Parallel installs** - UV installs packages in parallel automatically

## Why UV for This Project?

1. **Faster CI/CD** - Builds and tests run faster
2. **Better Development Experience** - Install dependencies in seconds
3. **Consistent Environment** - Better dependency resolution means fewer conflicts
4. **Future-Proof** - UV is actively developed and improving

## Resources

- **Official Website**: https://github.com/astral-sh/uv
- **Documentation**: https://github.com/astral-sh/uv#readme
- **Comparison with pip**: https://github.com/astral-sh/uv#uv-vs-pip

## Summary

UV makes this project:
- ⚡ **Faster** to install and run
- 🎯 **Easier** to manage dependencies
- 💾 **Smaller** disk footprint
- 🔧 **More reliable** with better dependency resolution

All Makefile commands now use UV automatically, so you get these benefits without any extra work!

---

**Pro Tip:** You don't need to know UV to use this project. Just run `make install` and everything works!
