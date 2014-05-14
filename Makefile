.PHONY: all clean test

all: test

clean:
	rm -rf .tox .coverage *.egg *.egg-info
	find -name '*.pyc' -exec rm -f {} +
	find -name '__pycache__' -exec rmdir -v {} +

test: clean
	coverage erase
	coverage run $(shell which nosetests)
	coverage report --show-missing --include=replay*
