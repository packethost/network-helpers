TEST_ROOT=/opt/tests
BIRD_PATH=$(TEST_ROOT)/bird

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
	black --check $(TEST_ROOT)

.PHONY: test-bird
test-bird:
	pip install -r $(BIRD_PATH)/requirements.txt
	mypy $(BIRD_PATH) --config-file $(BIRD_PATH)/pytest.ini
	PYTHONPATH=$(BIRD_PATH) cd $(BIRD_PATH); python -m pytest --cov --pylama --verbose --color=yes

all: lint test-bird
