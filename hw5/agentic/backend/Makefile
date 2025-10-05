.PHONY: help install run dev users list show clean clear-all clear-user clear-user-force clear-all-force

VENV = .venv
PYTHON = $(VENV)/bin/python
PIP = $(VENV)/bin/pip
UVICORN = $(VENV)/bin/uvicorn

ifneq (,$(wildcard .env))
    include .env
    export
endif

help:
	@echo "Available commands:"
	@echo "  make install              - Install dependencies from requirements.txt"
	@echo "  make run                  - Start the FastAPI server"
	@echo "  make dev                  - Start the server in development mode with reload"
	@echo "  make users                - List all users with conversations"
	@echo "  make list USER=<id>       - List all conversations for a user"
	@echo "  make show CONV=<id>       - Show all messages in a conversation"
	@echo "  make clear-user USER=<id> - Clear all conversations for a specific user"
	@echo "  make clear-all            - Clear all conversations for all users"
	@echo "  make clear-all-force      - Clear all conversations without confirmation"
	@echo "  make clean                - Remove cache files and temporary files"

install:
	$(PIP) install -r requirements.txt

run:
	$(UVICORN) src.main:app --env-file .env

dev:
	$(UVICORN) src.main:app --reload --env-file .env

users:
	$(PYTHON) -m src.cli list-users

list:
ifndef USER
	@echo "Error: USER is required. Usage: make list USER=user-1"
	@exit 1
endif
	$(PYTHON) -m src.cli list-conversations $(USER)

show:
ifndef CONV
	@echo "Error: CONV is required. Usage: make show CONV=1"
	@exit 1
endif
	$(PYTHON) -m src.cli show-messages $(CONV)

clear-user:
ifndef USER
	@echo "Error: USER is required. Usage: make clear-user USER=user-1"
	@exit 1
endif
	$(PYTHON) -m src.cli clear-conversations --user-id $(USER)

clear-user-force:
ifndef USER
	@echo "Error: USER is required. Usage: make clear-user-force USER=user-1"
	@exit 1
endif
	$(PYTHON) -m src.cli clear-conversations --user-id $(USER) -y

clear-all:
	$(PYTHON) -m src.cli clear-conversations

clear-all-force:
	$(PYTHON) -m src.cli clear-conversations -y

clean:
	find . -type f -name '*.pyc' -delete
	find . -type d -name '__pycache__' -delete
	find . -type d -name '*.egg-info' -exec rm -rf {} +
