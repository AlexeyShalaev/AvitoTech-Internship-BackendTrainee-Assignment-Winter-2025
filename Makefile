args := $(wordlist 2, 2, $(MAKECMDGOALS))
SERVICE := $(word 2, $(MAKECMDGOALS))
SERVICES_DIR := services/$(SERVICE)

ifndef SERVICE
MESSAGE = "No service specified. Usage: make <command> <service>"
else ifeq ($(words $(MAKECMDGOALS)), 2)
MESSAGE = "Done"
else
MESSAGE = "Invalid number of arguments. Usage: make <command> <service>"
endif

CODE = src tests

HELP_FUN = \
	%help; while(<>){push@{$$help{$$2//'options'}},[$$1,$$3] \
	if/^([\w-_]+)\s*:.*\#\#(?:@(\w+))?\s(.*)$$/}; \
    print"$$_:\n", map"  $$_->[0]".(" "x(20-length($$_->[0])))."$$_->[1]\n",\
    @{$$help{$$_}},"\n" for keys %help; \

# Commands
help: ##@Help Show this help
	@echo -e "Usage: make [command] [service] ...\n"
	@perl -e '$(HELP_FUN)' $(MAKEFILE_LIST)

run: ##@Service Run service
	docker compose -f docker-compose.yml up --build $(SERVICE)

test: ##@Service Run tests
	docker compose -f docker-compose-test.yml up --build $(SERVICE)-test

run-all: ##@Service Run service
	docker compose -f docker-compose.yml up --build

test-all: ##@Service Run tests
	docker compose -f docker-compose-test.yml up --build

lint: ##@Code Check code with pylint
	cd $(SERVICES_DIR) && python -m pylint $(CODE)

format: ##@Code Reformat code with isort and black
	cd $(SERVICES_DIR) && python -m isort $(CODE)
	cd $(SERVICES_DIR) && python -m black $(CODE)

clean: ##@Code Clean directory from garbage files
	cd $(SERVICES_DIR) && rm -fr *.egg-info dist

%::
	echo $(MESSAGE)