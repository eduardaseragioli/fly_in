PYTHON = python3
PIP = pip
MAIN = fly_in.py

all: intall 

intall:
	$(PIP) install -r $()

run:
	$(PYTHON) $(MAIN)

debug:
