PIPENV_VENV_IN_PROJECT := 1

.PHONY: clean help

PYTHON_VERSION ?= 3.6

help:
	@echo "These are our make targets and what they do."
	@echo "All unlisted targets are internal."
	@echo ""
	@echo "  help:      Show this helptext"
	@echo "  install:   Install requirements"
	@echo "  dev:       Setup environment for development"
	@echo "  clean:     Typical cleanup, scrub the installation"


Pipfile.lock: Pipfile
	pipenv lock --python $(PYTHON_VERSION)

.venv: Pipfile.lock
	pipenv sync --python $(PYTHON_VERSION)
	pipenv clean

.venv/bin/fair-identifiers-client: .venv
	pipenv run python setup.py install

install: .venv/bin/fair-identifiers-client
	ln -sf .venv/bin/fair-identifiers-client .

.venv/bin/pyls: Pipfile.lock
	pipenv sync --dev --python $(PYTHON_VERSION)
	pipenv clean

dev: .venv/bin/pyls
	pipenv run python setup.py develop

clean:
	pipenv --rm
	find -name '*.pyc' -delete
	-rm fair-identifiers-client
	-rm -r build
	-rm -r dist
	-rm -r *.egg-info
