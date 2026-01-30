# Makefile for Network Discovery Tool (Linux/macOS)

.PHONY: help install setup config clean test run discover serve export stats shell db-init lint format check-deps docs

# Variables
PYTHON := python3
PIP := $(PYTHON) -m pip
VENV := venv
VENV_BIN := $(VENV)/bin
VENV_PYTHON := $(VENV_BIN)/python
VENV_PIP := $(VENV_BIN)/pip

# Colors for output
RED := \033[0;31m
GREEN := \033[0;32m
YELLOW := \033[1;33m
BLUE := \033[0;34m
NC := \033[0m # No Color

##@ Help

help: ## Display this help message
	@echo "$(BLUE)Network Discovery Tool - Makefile Commands$(NC)"
	@echo ""
	@awk 'BEGIN {FS = ":.*##"; printf "Usage:\n  make $(CYAN)<target>$(NC)\n"} /^[a-zA-Z_0-9-]+:.*?##/ { printf "  $(CYAN)%-15s$(NC) %s\n", $$1, $$2 } /^##@/ { printf "\n$(YELLOW)%s$(NC)\n", substr($$0, 5) } ' $(MAKEFILE_LIST)

##@ Setup

install: ## Full installation (create venv, install deps, setup config)
	@echo "$(GREEN)Starting installation...$(NC)"
	@$(MAKE) venv
	@$(MAKE) deps
	@$(MAKE) package
	@$(MAKE) config
	@echo "$(GREEN)✓ Installation complete!$(NC)"
	@echo "$(YELLOW)Next steps:$(NC)"
	@echo "  1. Edit config/devices.yaml with your network details"
	@echo "  2. Set SSH password: export SSH_PASSWORD='your-password'"
	@echo "  3. Run discovery: make discover"

venv: ## Create virtual environment
	@echo "$(BLUE)Creating virtual environment...$(NC)"
	@test -d $(VENV) || $(PYTHON) -m venv $(VENV)
	@echo "$(GREEN)✓ Virtual environment created$(NC)"

deps: ## Install dependencies
	@echo "$(BLUE)Installing dependencies...$(NC)"
	@$(VENV_PIP) install --upgrade pip setuptools wheel
	@$(VENV_PIP) install -r requirements.txt
	@echo "$(GREEN)✓ Dependencies installed$(NC)"

package: ## Install package in development mode
	@echo "$(BLUE)Installing package...$(NC)"
	@$(VENV_PIP) install -e .
	@echo "$(GREEN)✓ Package installed$(NC)"

config: ## Create configuration files from templates
	@echo "$(BLUE)Setting up configuration...$(NC)"
	@if [ ! -f config/devices.yaml ]; then \
		cp config/devices.yaml.example config/devices.yaml; \
		echo "$(GREEN)✓ Created config/devices.yaml$(NC)"; \
		echo "$(YELLOW)⚠ Please edit config/devices.yaml with your network details$(NC)"; \
	else \
		echo "$(YELLOW)⚠ config/devices.yaml already exists$(NC)"; \
	fi
	@if [ ! -f .env ]; then \
		cp .env.example .env; \
		echo "$(GREEN)✓ Created .env$(NC)"; \
		echo "$(YELLOW)⚠ Please edit .env with your credentials$(NC)"; \
	else \
		echo "$(YELLOW)⚠ .env already exists$(NC)"; \
	fi
	@mkdir -p logs
	@echo "$(GREEN)✓ Configuration setup complete$(NC)"

setup: install ## Alias for install

##@ Discovery

discover: ## Run network discovery
	@echo "$(BLUE)Starting network discovery...$(NC)"
	@$(VENV_BIN)/network-discovery discover run
	@echo "$(GREEN)✓ Discovery complete$(NC)"

discover-verbose: ## Run discovery with verbose logging
	@echo "$(BLUE)Starting verbose network discovery...$(NC)"
	@LOG_LEVEL=DEBUG $(VENV_BIN)/network-discovery discover run
	@echo "$(GREEN)✓ Discovery complete$(NC)"

discover-shallow: ## Run discovery with max depth 3
	@echo "$(BLUE)Starting shallow discovery (max depth 3)...$(NC)"
	@$(VENV_BIN)/network-discovery discover run --max-depth 3
	@echo "$(GREEN)✓ Discovery complete$(NC)"

status: ## Show last discovery status
	@$(VENV_BIN)/network-discovery discover status

##@ Data Management

list-devices: ## List all discovered devices
	@$(VENV_BIN)/network-discovery list-devices

list-switches: ## List all switches
	@$(VENV_BIN)/network-discovery list-devices --type switch

list-connections: ## List all connections
	@$(VENV_BIN)/network-discovery list-connections

stats: ## Show topology statistics
	@$(VENV_BIN)/network-discovery stats

##@ Search

search-mac: ## Search for MAC address (usage: make search-mac MAC=aa:bb:cc:dd:ee:ff)
	@if [ -z "$(MAC)" ]; then \
		echo "$(RED)Error: MAC address required$(NC)"; \
		echo "Usage: make search-mac MAC=aa:bb:cc:dd:ee:ff"; \
		exit 1; \
	fi
	@$(VENV_BIN)/network-discovery search mac $(MAC)

search-device: ## Search for device (usage: make search-device DEVICE=hostname)
	@if [ -z "$(DEVICE)" ]; then \
		echo "$(RED)Error: Device name required$(NC)"; \
		echo "Usage: make search-device DEVICE=hostname"; \
		exit 1; \
	fi
	@$(VENV_BIN)/network-discovery search device $(DEVICE)

##@ Export

export-json: ## Export topology as JSON
	@echo "$(BLUE)Exporting topology to topology.json...$(NC)"
	@$(VENV_BIN)/network-discovery export --format json --output topology.json
	@echo "$(GREEN)✓ Exported to topology.json$(NC)"

export-graphml: ## Export topology as GraphML
	@echo "$(BLUE)Exporting topology to topology.graphml...$(NC)"
	@$(VENV_BIN)/network-discovery export --format graphml --output topology.graphml
	@echo "$(GREEN)✓ Exported to topology.graphml$(NC)"

export-all: export-json export-graphml ## Export topology in all formats
	@echo "$(GREEN)✓ All exports complete$(NC)"

##@ Web Server

serve: ## Start web dashboard server
	@echo "$(BLUE)Starting web dashboard...$(NC)"
	@echo "$(GREEN)API: http://localhost:5000$(NC)"
	@echo "$(GREEN)Dashboard: Open web/index.html in your browser$(NC)"
	@echo "$(YELLOW)Press Ctrl+C to stop$(NC)"
	@$(VENV_BIN)/network-discovery serve

serve-debug: ## Start web server in debug mode
	@echo "$(BLUE)Starting web dashboard in debug mode...$(NC)"
	@$(VENV_BIN)/network-discovery serve --debug

serve-public: ## Start web server accessible from network
	@echo "$(BLUE)Starting web dashboard on 0.0.0.0:5000...$(NC)"
	@echo "$(YELLOW)Server will be accessible from your network$(NC)"
	@$(VENV_BIN)/network-discovery serve --host 0.0.0.0 --port 5000

##@ Database

db-init: ## Initialize database
	@echo "$(BLUE)Initializing database...$(NC)"
	@$(VENV_PYTHON) -c "from src.database.schema import create_database; from src.utils.config import get_database_url; create_database(get_database_url())"
	@echo "$(GREEN)✓ Database initialized$(NC)"

db-shell: ## Open database shell
	@echo "$(BLUE)Opening database shell...$(NC)"
	@sqlite3 network_discovery.db

db-backup: ## Backup database
	@echo "$(BLUE)Backing up database...$(NC)"
	@cp network_discovery.db network_discovery.db.backup.$$(date +%Y%m%d_%H%M%S)
	@echo "$(GREEN)✓ Database backed up$(NC)"

db-clean: ## Remove database (WARNING: deletes all data)
	@echo "$(RED)WARNING: This will delete all discovered data!$(NC)"
	@read -p "Are you sure? (y/N): " confirm && [ "$$confirm" = "y" ] || exit 1
	@rm -f network_discovery.db
	@echo "$(GREEN)✓ Database removed$(NC)"

##@ Development

shell: ## Open Python shell with project context
	@echo "$(BLUE)Opening Python shell...$(NC)"
	@$(VENV_PYTHON) -i -c "from src.database.schema import *; from src.database.repository import *; from src.core.discovery.engine import *; from src.utils.config import *; print('Project modules loaded')"

test: ## Run tests
	@echo "$(BLUE)Running tests...$(NC)"
	@$(VENV_BIN)/pytest tests/ -v

test-cov: ## Run tests with coverage
	@echo "$(BLUE)Running tests with coverage...$(NC)"
	@$(VENV_BIN)/pytest tests/ -v --cov=src --cov-report=html --cov-report=term

lint: ## Run linter (flake8)
	@echo "$(BLUE)Running linter...$(NC)"
	@$(VENV_BIN)/flake8 src/ --max-line-length=100 --ignore=E501,W503

format: ## Format code with black
	@echo "$(BLUE)Formatting code...$(NC)"
	@$(VENV_BIN)/black src/ --line-length=100

format-check: ## Check code formatting
	@echo "$(BLUE)Checking code formatting...$(NC)"
	@$(VENV_BIN)/black src/ --check --line-length=100

type-check: ## Run type checking with mypy
	@echo "$(BLUE)Running type checker...$(NC)"
	@$(VENV_BIN)/mypy src/ --ignore-missing-imports

check: lint format-check type-check ## Run all checks

##@ Utilities

check-deps: ## Check for missing dependencies
	@echo "$(BLUE)Checking dependencies...$(NC)"
	@$(VENV_PIP) check

update-deps: ## Update all dependencies
	@echo "$(BLUE)Updating dependencies...$(NC)"
	@$(VENV_PIP) install --upgrade -r requirements.txt
	@echo "$(GREEN)✓ Dependencies updated$(NC)"

freeze: ## Freeze current dependencies
	@$(VENV_PIP) freeze > requirements.lock

docs: ## Open documentation
	@echo "$(BLUE)Opening documentation...$(NC)"
	@if command -v xdg-open > /dev/null; then \
		xdg-open README.md; \
	elif command -v open > /dev/null; then \
		open README.md; \
	else \
		echo "$(YELLOW)Please open README.md manually$(NC)"; \
	fi

logs: ## Show discovery logs
	@tail -f logs/discovery.log

##@ Cleanup

clean: ## Clean temporary files
	@echo "$(BLUE)Cleaning temporary files...$(NC)"
	@find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	@find . -type f -name "*.pyc" -delete
	@find . -type f -name "*.pyo" -delete
	@find . -type f -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	@rm -rf .pytest_cache .mypy_cache .coverage htmlcov/ 2>/dev/null || true
	@echo "$(GREEN)✓ Temporary files cleaned$(NC)"

clean-all: clean db-clean ## Clean everything including database
	@echo "$(BLUE)Cleaning everything...$(NC)"
	@rm -rf $(VENV)
	@rm -f topology.json topology.graphml topology.gexf
	@rm -rf logs/*.log
	@echo "$(GREEN)✓ Everything cleaned$(NC)"

##@ Production

prod-install: ## Install for production
	@echo "$(BLUE)Installing for production...$(NC)"
	@$(MAKE) venv
	@$(VENV_PIP) install --upgrade pip
	@$(VENV_PIP) install -r requirements.txt
	@$(VENV_PIP) install gunicorn
	@$(VENV_PIP) install -e .
	@echo "$(GREEN)✓ Production installation complete$(NC)"

prod-serve: ## Start production server with Gunicorn
	@echo "$(BLUE)Starting production server...$(NC)"
	@$(VENV_BIN)/gunicorn -w 4 -b 0.0.0.0:5000 'api.app:create_app()'

##@ Quick Start

quickstart: install discover serve ## Complete quickstart (install, discover, serve)
	@echo "$(GREEN)✓ Quickstart complete!$(NC)"

demo: ## Run a demo discovery (requires demo config)
	@echo "$(BLUE)Running demo...$(NC)"
	@echo "$(YELLOW)This is a simulation. Configure real devices in config/devices.yaml$(NC)"

.DEFAULT_GOAL := help
