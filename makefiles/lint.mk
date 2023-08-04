.PHONY: lint lint-flake8 lint-pylint lint-black black

lint : lint lint-flake8 lint-pylint lint-black black

lint-flake8 :
	flake8 --count --statistics app/ *.py

lint-pylint :
	pylint --jobs 0 app/ *.py

lint-black :
	black --check --diff --verbose app/ *.py

black :
	black app/ *.py