.PHONY: clean-pyc
clean-pyc:
	-find . -name '*.pyc' -delete
	-find . -name '*.pyo' -delete
	-find . -name '*~' -delete
	-find . -name '.mypy_cache' | xargs rm -rf
	-find . -name '.pytest_cache' | xargs rm -rf
	-find . -name '__pycache__' | xargs rm -rf

.PHONY: lint
lint: clean-pyc
	black --check /opt/tests

.PHONY: test-bird
test-bird:
	mypy /opt/tests/bird --config-file /opt/tests/bird/pytest.ini

all: lint test-bird
