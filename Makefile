.PHONY: test install-dev run_server  run_client clean

all: test

install-dev:
	pip3 install -q -e .

test: clean install-dev
	pytest

run_server: install-dev
	python3 compression_service/server.py 4000

run_client: install-dev
	python3 test/interactive_client.py localhost 4000

# Remove auto-generated files
clean:
	find . -name '*.pyc' -exec rm -f {} +
	find . -name '*.pyo' -exec rm -f {} +
	find . -name '*~' -exec rm -f {} +
	find . -name '.DS_Store' -exec rm -f {} +
	rm -rf .pytest_cache
	rm -rf test/__pycache__
	rm -rf compression_service/__pycache__
	rm -rf compression_service.egg-info
