.PHONY: help setup test lint demo doctor score clean

help:
	@echo "Ultimate Best Seller Studio"
	@echo ""
	@echo "  make setup    Initialize the Better Humanizer submodule + dev install"
	@echo "  make test     Run the test suite"
	@echo "  make lint     Run ruff"
	@echo "  make doctor   Check the checkout is ready to run"
	@echo "  make demo     Build a deterministic mechanical demo project in ./.demo"
	@echo "  make score    Human-band score the demo project (needs the submodule)"
	@echo "  make clean    Remove build/demo artifacts"

setup:
	git submodule update --init --recursive
	python3 -m pip install -e ".[dev]"

test:
	python3 -m pytest -q || python3 -m unittest tests.test_runner tests.test_humanband tests.test_doctor

lint:
	ruff check runner tests

doctor:
	python3 -m runner.cli doctor

demo:
	rm -rf .demo && python3 -m runner.cli demo .demo

score: demo
	python3 -m runner.cli humanize-score .demo --register literary

clean:
	rm -rf .demo build dist *.egg-info
	find . -name __pycache__ -type d -prune -exec rm -rf {} +
