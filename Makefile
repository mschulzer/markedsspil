## ----------------------------------------------------------------------
## Makefile for Markedsspillet.dk
##
## Used for both development and production. See targets below.
## ----------------------------------------------------------------------

help:   # Show this help.
	@sed -ne '/@sed/!s/## //p' $(MAKEFILE_LIST)

# ---------- Development ---------- #
build:  ## Build or rebuild development docker image
	docker-compose -f docker-compose.dev.yml build

develop:  ## Run development server
	docker-compose -f docker-compose.dev.yml up --remove-orphans

# ---------- Checks and tests ---------- #
test: ## Execute tests within the docker image
	docker-compose run --rm web django-admin compilemessages
	DJANGO_SETTINGS_MODULE=config.settings docker-compose run --rm web pytest 


flake8: ## PEP8 codestyle check
	flake8 --exclude market/migrations --extend-exclude accounts/migrations

# This target runs both PEP8 checks and test suite
check: flake8 test

tidy:   ## Reformat source files to adhere to PEP8 
	black -79 . --exclude=market/migrations --extend-exclude=accounts/migrations


# ---------- Production ---------- #
production_stop: ## Stop production server
	docker-compose -f docker-compose.prod.yml down --remove-orphans

production_start: ## Start production server as daemon
	docker-compose -f docker-compose.prod.yml up --build --remove-orphans -d

production_djangologs: ## Show django logs
	docker logs markedsspilletdk_web_1

production_accesslogs: ## Show nginx access logs
	docker logs markedsspilletdk_nginx_1

# Open shell within running docker development container
shell:
	docker-compose exec web /bin/bash
