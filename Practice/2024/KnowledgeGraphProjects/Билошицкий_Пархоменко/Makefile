# Python version and virtualenv settings
PYTHON = python3
VENV = .venv
VENV_BIN = $(VENV)/bin
VENV_ACTIVATE = $(VENV_BIN)/activate

# Requirements file
REQUIREMENTS = requirements.txt

.PHONY: all setup clean run-parsers run-ontology run-embeddings

all: setup run-parsers run-ontology run-embeddings

# Create virtual environment and install dependencies
setup: $(VENV)/touchfile

$(VENV)/touchfile: $(REQUIREMENTS)
	$(PYTHON) -m venv $(VENV)
	. $(VENV_ACTIVATE) && pip install -r $(REQUIREMENTS)
	touch $(VENV)/touchfile

# Run the parsers
run-parsers:
	. $(VENV_ACTIVATE) && PYTHONPATH=./src $(PYTHON) -m src.parsers.run_all_parsers

# Run the ontology script
run-ontology:
	. $(VENV_ACTIVATE) && PYTHONPATH=./src $(PYTHON) -m src.ontology.minecraft_ontology

# Run the embedding script
run-embeddings:
	. $(VENV_ACTIVATE) && PYTHONPATH=./src $(PYTHON) -m src.embedding.main

# Clean up virtual environment
clean:
	rm -rf $(VENV)
	find . -type f -name '*.pyc' -delete
	find . -type d -name '__pycache__' -delete 