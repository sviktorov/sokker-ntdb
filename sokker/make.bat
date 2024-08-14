.ONESHELL:
# XXX: Bamboo pipeline fails when using bash as the shell
SHELL := sh
# .SHELLFLAGS := -eu -o pipefail -c

COMMIT=$(shell git rev-parse HEAD)
RELEASE=psp-$(COMMIT).tar

archive:
	git archive $(COMMIT) -o $(RELEASE)

tox-deps: test/requirements.txt

test/requirements.txt: requirements.txt
	sed '/django==/d' requirements.txt > $@
	sed '/django-cms==/d' $@ > $@

compile: 
	pip-compile

compile-dev:	
	pip-compile requirements-dev.in

.PHONY: archive lock tox-deps test test-all

# see pytest.ini for config
test:
	pytest -x

test-all:
	pytest

fmt:
	black .
