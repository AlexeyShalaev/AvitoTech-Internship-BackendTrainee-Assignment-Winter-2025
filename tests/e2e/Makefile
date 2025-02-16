args := $(wordlist 2, 100, $(MAKECMDGOALS))
ifndef args
MESSAGE = "No such command (or you pass two or many targets to ). List of possible commands: make help"
else
MESSAGE = "Done"
endif

HELP_FUN = \
	%help; while(<>){push@{$$help{$$2//'options'}},[$$1,$$3] \
	if/^([\w-_]+)\s*:.*\#\#(?:@(\w+))?\s(.*)$$/}; \
    print"$$_:\n", map"  $$_->[0]".(" "x(20-length($$_->[0])))."$$_->[1]\n",\
    @{$$help{$$_}},"\n" for keys %help; \

# Commands
help: ##@Help Show this help
	@echo -e "Usage: make [command] [service] ...\n"
	@perl -e '$(HELP_FUN)' $(MAKEFILE_LIST)

infra: ##@Tests Run infra
	docker compose -f ../../docker-compose.yml up --build -d

install: ##@Tests Install raw dependencies
	poetry install --no-interaction --no-ansi --all-extras

test: ##@Tests Run tests
	poetry run pytest tests

%::
	echo $(MESSAGE)
