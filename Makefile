SHELL := /bin/bash

formatted_code := app/ migrations/ tests/
rev_id = ""
migration_message = ""

.ONESHELL:

.PHONY: test run

requirements.txt: requirements.in
	pip-compile --quiet --generate-hashes --output-file=$@

format:
	isort $(formatted_code)
	black $(formatted_code)

lint:
	pylint app

run:
	python -m app --reload

make run-container:
	docker-compose up -d


test: build
	function removeContainers {
		docker-compose -p rundapp-api-continuous-integration rm -s -f test_db
	}
	trap removeContainers EXIT
	docker-compose -p rundapp-api-continuous-integration run --rm continuous-integration


migration:
	if [ -z $(rev_id)] || [ -z $(migration_message)]; \
	then \
		echo -e "\n\nmake migration requires both a rev_id and a migration_message.\nExample usage: make migration rev_id=0001 migration_message=\"my message\"\n\n"; \
	else \
		alembic revision --autogenerate --rev-id "$(rev_id)" -m "$(migration_message)"; \
	fi

migrate:
	alembic upgrade head