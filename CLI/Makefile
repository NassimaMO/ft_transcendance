VENV_DIR := myenv
PYTHON := $(VENV_DIR)/bin/python
PIP := $(VENV_DIR)/bin/pip
REQUIREMENTS := requirements.txt
SCRIPT := main.py

all: run

$(VENV_DIR):
	python3 -m venv $(VENV_DIR)

install: $(VENV_DIR)
	$(PIP) install --upgrade pip
	$(PIP) install -r $(REQUIREMENTS)

run: install
	$(PYTHON) $(SCRIPT)

clean:
	rm -rf $(VENV_DIR)

fclean: clean
	find . -type d -name "__pycache__" -exec rm -r {} +
	find . -type f -name "*.pyc" -delete

.PHONY: all install run clean fclean help