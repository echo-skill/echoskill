.PHONY: venv test clean

venv:
	@if [ ! -d ".venv" ]; then \
		python3 -m venv .venv && \
		. .venv/bin/activate && pip install --upgrade pip && pip install -e '.[dev]'; \
	fi

test: venv
	@. .venv/bin/activate && pytest

clean:
	rm -rf .venv .pytest_cache
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
