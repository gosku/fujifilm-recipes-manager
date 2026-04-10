VENV    := .venv
PYTHON  := $(VENV)/bin/python
PIP     := $(VENV)/bin/pip
PYTEST  := $(VENV)/bin/pytest
CELERY  := $(VENV)/bin/celery

ENV_FILE := src/config/env

.PHONY: setup env run worker test help

## setup   — create venv, install deps, generate env file, run migrations
setup: $(VENV)/.deps-installed env
	@echo "[setup] Running database migrations..."
	@$(PYTHON) manage.py migrate
	@echo ""
	@echo "Done. Run 'make run' to start the server."

## env     — generate src/config/env from settings defaults (skips if already exists)
env:
	@if [ ! -f $(ENV_FILE) ]; then \
		echo "[env] Generating $(ENV_FILE) from settings defaults..."; \
		python3 -c "$$GENERATE_ENV"; \
		echo "[env] $(ENV_FILE) written — edit it to customise your installation"; \
	else \
		echo "[skip] $(ENV_FILE) already exists"; \
	fi

define GENERATE_ENV
import re
content = open("src/config/settings.py").read()
pattern = r'env\.\w+\(\s*"(\w+)"\s*,\s*default=([^)]+)\)'
lines = []
for name, raw in re.findall(pattern, content):
    val = raw.strip().strip('"')
    lines.append(name + "=" + val)
open("src/config/env", "w").write("\n".join(lines) + "\n")
endef
export GENERATE_ENV

# Re-run pip only when requirements.txt changes (sentinel file tracks this).
$(VENV)/.deps-installed: requirements.txt $(VENV)/bin/activate
	@echo "[setup] Installing Python dependencies..."
	@$(PIP) install --quiet -r requirements.txt
	@touch $@

$(VENV)/bin/activate:
	@echo "[setup] Creating virtual environment..."
	@python3 -m venv $(VENV)

## run     — start the Django development server
run:
	$(PYTHON) manage.py runserver

## worker  — start a Celery worker (requires RabbitMQ)
worker:
	$(CELERY) -A src.config worker --loglevel=info --concurrency=8

## test    — run the test suite
test:
	$(PYTEST)

## help    — list available targets
help:
	@grep -E '^## ' Makefile | sed 's/^## //'
