VENV_PY := $(abspath .venv/bin/python)
PYTHONPATH := $(abspath .)

.PHONY: help seed-books populate-authors remove-books remove-authors

help:
	@echo "Available targets: seed-books populate-authors remove-books remove-authors"

# allow override: make seed-books COUNT=50
COUNT ?= 100

seed-books:
	@echo "Seeding books ($(COUNT)) using venv $(VENV_PY)"
	PYTHONPATH=$(PYTHONPATH)/server $(VENV_PY) -m src.cli seed-books --count $(COUNT)

populate-authors:
	@echo "Populating default authors and book authors"
	PYTHONPATH=$(PYTHONPATH)/server $(VENV_PY) -m src.cli populate-authors --include-book-authors

remove-books:
	@echo "Removing all books"
	PYTHONPATH=$(PYTHONPATH)/server $(VENV_PY) -m src.cli remove-books --all

remove-authors:
	@echo "Removing all authors"
	PYTHONPATH=$(PYTHONPATH)/server $(VENV_PY) -m src.cli remove-authors --all
