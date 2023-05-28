THIS_FILE := $(lastword $(MAKEFILE_LIST))
.PHONY: help build up start down destroy stop restart logs logs-api ps login-timescale login-api db-shell test
build:
	docker-compose -f docker-compose.yml build $(c)
help:
	make -pRrq  -f $(THIS_FILE) : 2>/dev/null | awk -v RS= -F: '/^# File/,/^# Finished Make data base/ {if ($$1 !~ "^[#.]") {print $$1}}' | sort | egrep -v -e '^[^[:alnum:]]' -e '^$@$$'
up:
	docker-compose -f docker-compose.yml up -d $(c)
start:
	docker-compose -f docker-compose.yml start $(c)
down:
	docker-compose -f docker-compose.yml down $(c)
destroy:
	docker-compose -f docker-compose.yml down -v $(c)
stop:
	docker-compose -f docker-compose.yml stop $(c)
restart:
	docker-compose -f docker-compose.yml stop $(c)
	docker-compose -f docker-compose.yml up -d $(c)
logs:
	docker-compose -f docker-compose.yml logs --tail=100 -f $(c)
logs-web:
	docker-compose -f docker-compose.yml logs --tail=100 -f web
ps:
	docker-compose -f docker-compose.yml ps
login-db:
	docker-compose -f docker-compose.yml exec db /bin/bash
login-web:
	docker-compose -f docker-compose.yml exec web /bin/bash
db-shell:
	docker-compose -f docker-compose.yml exec db psql -Upostgres
test:
	python ./test/test_send_file.py
