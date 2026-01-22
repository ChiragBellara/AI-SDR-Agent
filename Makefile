.PHONY: setup sync playwright test clean

sync:
	uv sync

playwright:
	uv run playwright install

setup: sync playwright

clean:
	rm -rf .venv

help:
	@echo "Available commands:"
	@echo "  make setup     Install dependencies + Playwright browsers"
	@echo "  make test      Run tests"
	@echo "  make clean     Remove virtual environment"
	@echo "  make help      Show this help message"