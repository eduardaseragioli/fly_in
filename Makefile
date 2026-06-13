VENV_DIR = venv
VENV_BIN = $(VENV_DIR)/bin
PYTHON = $(VENV_BIN)/python3
PIP = $(VENV_BIN)/pip

MAIN = srcs/main.py
#FILE = maps/easy/01_linear_path.txt
#FILE = maps/challenger/01_the_impossible_dream.txt
#FILE = maps/hard/01_maze_nightmare.txt
#FILE = maps/easy/02_simple_fork.txt
FILE = maps/medium/03_priority_puzzle.txt
REQS = requirements.txt

all: install 

$(VENV_BIN)/activate:
	@echo "Creating virtual environment"
	python3 -m venv $(VENV_DIR)


install: $(VENV_BIN)/activate
	@echo "Install dependencies(mypy, flake8, pygame)"
	@$(PIP) install --upgrade pip
	@$(PIP) install flake8 mypy
	@$(PIP) install pygame
	@echo "everything installed"

run:
	$(PYTHON) $(MAIN) $(FILE)

visual: install
	$(PYTHON) $(MAIN) $(FILE) --visual

debug:
	$(PYTHON) -m pdb $(MAIN) $(FILE)

lint:
	flake8 .
	mypy . --warn-return-any \
	--warn-unused-ignores \
	--ignore-missing-imports \
	--disallow-untyped-defs \
	--check-untyped-defs

clean:
	rm -rf __pycache__ .mypy_cache

fclean: clean
	rm -fr $(VENV_DIR)

.PHONY: all install run visual debug lint clean fclean