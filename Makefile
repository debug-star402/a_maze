PYTHON = python3
MAIN = a_maze_ing.py
CONFIG = config.txt
.PHONY: all install run debug clean lint lint-strict

all: run

install:
	$(PYTHON) -m pip install -r requirements.txt

run:
	$(PYTHON) $(MAIN) $(CONFIG)

debug:
	$(PYTHON) -m pdb $(MAIN) $(CONFIG)

clean:
	rm -rf __pycache__
	rm -rf mazegen/__pycache__
	rm -rf .mypy_cache
	rm -rf build
	rm -rf dist
	rm -rf mazegen.egg-info

lint:
	flake8 .
	mypy --warn-return-any --warn-unused-ignores --ignore-missing-imports --disallow-untyped-defs --check-untyped-defs .

lint-strict:
	flake8 .
	mypy --strict .