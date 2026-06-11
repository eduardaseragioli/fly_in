PYTHON = python3
PIP = pip
MAIN = srcs/main.py
FILE = maps/hard/02_capacity_hell.txt
REQS = requirements.txt


all: install 

install:
	$(PIP) install -r $(REQS)

run:
	$(PYTHON) $(MAIN) $(FILE)

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

.PHONY: all install run debug lint clean