# Run development server
runserver:
	docker-compose up

# Execute tests within the docker image
test:
	docker-compose run --rm web ./manage.py test

# Rebuild docker image
build:
	docker-compose build

# Open shell within running docker development container
shell:
	docker-compose exec web /bin/bash
