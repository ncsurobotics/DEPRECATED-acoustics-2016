
all: clean-pyc

# test:

# clean:


clean-pyc:
	find . -name '*.py[co]' -delete
	find . -name '*__pycache__' -delete