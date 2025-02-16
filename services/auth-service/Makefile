args := $(wordlist 2, 100, $(MAKECMDGOALS))
ifndef args
MESSAGE = "No such command (or you pass two or many targets to ). List of possible commands: make help"
else
MESSAGE = "Done"
endif

CODE = src tests

HELP_FUN = \
	%help; while(<>){push@{$$help{$$2//'options'}},[$$1,$$3] \
	if/^([\w-_]+)\s*:.*\#\#(?:@(\w+))?\s(.*)$$/}; \
    print"$$_:\n", map"  $$_->[0]".(" "x(20-length($$_->[0])))."$$_->[1]\n",\
    @{$$help{$$_}},"\n" for keys %help; \

# Commands
help: ##@Help Show this help
	@echo -e "Usage: make [target] ...\n"
	@perl -e '$(HELP_FUN)' $(MAKEFILE_LIST)

lint:  ##@Code Check code with pylint
	python -m pylint $(CODE)

fmt:  ##@Code Reformat code with isort and
	python -m isort $(CODE)
	python -m black $(CODE)

clean:  ##@Code Clean directory from garbage files
	rm -fr *.egg-info dist *.pyc
	find . -name \*.pyc -delete
	find . -name __pycache__ -delete
	find . -name run -delete
	find . -name \*.a -delete

req-install: ##@App Install dependencies
	pip install poetry-add-requirements.txt
	poeareq  requirements.txt
	poeareq  tests/requirements.txt

install: ##@App Install raw dependencies
	poetry install --no-interaction --no-ansi --all-extras

run:	##@App Run application
	poetry run python src/main.py

test:	##@App Test application
	poetry run pytest tests

%::
	echo $(MESSAGE)
