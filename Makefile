SHELL = /bin/bash

# Use `config.yaml` by default, unless overridden by user
# through setting FLAGS environment variable
FLAGS:=$(if $(FLAGS),$(FLAGS),--config=config.yaml)

PYTHON=PYTHONPATH=. python

SUPERVISORD_CFG=services/supervisor.conf
SUPERVISORD=$(PYTHON) -m supervisor.supervisord -s -c $(SUPERVISORD_CFG)
SUPERVISORCTL=$(PYTHON) -m supervisor.supervisorctl -c $(SUPERVISORD_CFG)

# Bold
B=\033[1m
# Normal
N=\033[0m

paths:
	@mkdir -p log run tmp
	@mkdir -p ./log/sv_child

system_setup: | paths

run: ## Start the app
run: FLAGS:=$(FLAGS) --debug
run: system_setup
	@echo
	$(call LOG, Starting micro-services)
	@echo
	@echo " - Run \`make log\` in another terminal to view logs"
	@echo " - Run \`make monitor\` in another terminal to restart services"
	@echo
	@echo "The server is in debug mode:"
	@echo
	@export FLAGS="$(FLAGS)" && \
	echo "Press Ctrl-C to abort the server" && \
	echo && \
	$(SUPERVISORD)

monitor: ## Monitor microservice status.
	@echo "Entering supervisor control panel."
	@echo
	@echo " - Type \`status\` to see microservice status"
	@echo
	@$(SUPERVISORCTL) -i
