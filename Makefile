TEST_ROOT=/opt/tests
ROUTERS_PATH=$(TEST_ROOT)/routers
BIRD_PATH=$(TEST_ROOT)/routers/bird
FRR_PATH=$(TEST_ROOT)/routers/frr

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
	mypy $(BIRD_PATH) --config-file $(BIRD_PATH)/pytest.ini
	cd $(BIRD_PATH); python -m pytest --cov --pylama --verbose --color=yes

all: lint test-bird
