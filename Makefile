.PHONY: setup run build clean lint lint-fix package smoke test check

.DEFAULT_GOAL := check

# Release artifacts are named fithit-cli-<version>-<os>-<arch>.tar.gz.
# The binary is always built for the host platform; cross-compiling is not
# supported by PyInstaller, so each target gets its own CI runner.
UNAME_S := $(shell uname -s)
UNAME_M := $(shell uname -m)

ifeq ($(UNAME_S),Darwin)
	TARGET_OS := macos
	SHA256 := shasum -a 256
else
	TARGET_OS := linux
	SHA256 := sha256sum
endif

ifneq ($(filter $(UNAME_M),arm64 aarch64),)
	TARGET_ARCH := arm64
else
	TARGET_ARCH := x86_64
endif

VERSION ?= $(shell grep '^version' pyproject.toml | head -1 | cut -d'"' -f2)
TARBALL := fithit-cli-$(VERSION)-$(TARGET_OS)-$(TARGET_ARCH).tar.gz

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
	uv run pyinstaller --clean --noconfirm fithit.spec

package: build
	@set -e; \
	echo "Packaging fithit v$(VERSION) for $(TARGET_OS)/$(TARGET_ARCH)..."; \
	cd dist && \
	COPYFILE_DISABLE=1 tar -czf "$(TARBALL)" fithit && \
	$(SHA256) "$(TARBALL)"

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
