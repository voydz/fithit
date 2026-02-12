.PHONY: setup run build clean lint lint-fix package smoke test check

.DEFAULT_GOAL := check

setup:
	uv venv
	uv sync --extra dev

run:
	uv run fithit

lint:
	uv run ruff check src/
	uv run ruff format --check src/

lint-fix:
	uv run ruff check --fix src/
	uv run ruff format src/

test:
	uv run pytest

check: lint test

build:
	uv run pyinstaller \
		--onefile \
		--name fithit \
		--target-arch arm64 \
		--collect-all rich \
		src/fithitcli/__main__.py

package: build
	@set -e; \
	VERSION=$$(grep '^version' pyproject.toml | head -1 | cut -d'"' -f2); \
	echo "Packaging fithit v$$VERSION..."; \
	cd dist && \
	tar -czf "fithit-cli-$$VERSION-macos.tar.gz" fithit && \
	shasum -a 256 "fithit-cli-$$VERSION-macos.tar.gz"

smoke: build
	@set -e; \
	tmp_home="$$(mktemp -d)"; \
	trap 'rm -rf "$$tmp_home"' EXIT; \
	env -i PATH="/usr/bin:/bin:/usr/sbin:/sbin" HOME="$$tmp_home" \
		PYTHONNOUSERSITE=1 PYTHONPATH= PYTHONHOME= \
		VIRTUAL_ENV= CONDA_PREFIX= CONDA_DEFAULT_ENV= PIPENV_ACTIVE= \
		PYENV_VERSION= UV_PROJECT_ENV= \
		./dist/fithit --help

clean:
	rm -rf dist build __pycache__ src/fithitcli/__pycache__
