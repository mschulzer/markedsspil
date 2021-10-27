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

shell:  ## Open shell in running docker development container
	docker-compose -f docker-compose.dev.yml exec web /bin/bash

develop_create_backup:	## Create backup of development database
	docker-compose -f docker-compose.dev.yml run --rm pgbackups /backup.sh

migrations: # make migrations
	docker-compose -f docker-compose.dev.yml exec web python manage.py makemigrations

migrate: # make migrations
	docker-compose -f docker-compose.dev.yml exec web python manage.py migrate


# ---------- Checks and tests ---------- #
test: ## Execute tests within the docker image
	docker-compose -f docker-compose.dev.yml run --rm web django-admin compilemessages
	DJANGO_SETTINGS_MODULE=config.settings docker-compose -f docker-compose.dev.yml run --rm web pytest

test_functional: ## run test suite in test_functional.py
	docker-compose -f docker-compose.dev.yml run web pytest market/tests/test_functional.py

test_forms: ## run test suite in test_forms.py
	docker-compose -f docker-compose.dev.yml run web pytest market/tests/test_forms.py

test_views: ## run test suite in test_views.py
	docker-compose -f docker-compose.dev.yml run web pytest market/tests/test_views.py

test_helpers: ## run test suite in test_helpers.py
	docker-compose -f docker-compose.dev.yml run web pytest market/tests/test_helpers.py

test_models: ## run test suite in test_helpers.py
	docker-compose -f docker-compose.dev.yml run web pytest market/tests/test_helpers.py

test_factories: ## run test suite in test_helpers.py
	docker-compose -f docker-compose.dev.yml run web pytest market/tests/test_factories.py


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

production_shell: # Open shell in running docker production container
	docker-compose -f docker-compose.prod.yml exec web /bin/bash

production_create_backup: ## Create a database backup manually
	docker-compose -f docker-compose.prod.yml run --rm pgbackups /backup.sh
