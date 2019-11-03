ui_version := 0.2
SHELL := /bin/bash
AWS_ACCESS_KEY_ID := $(shell aws configure get aws_access_key_id)
AWS_SECRET_ACCESS_KEY := $(shell aws configure get aws_secret_access_key)
AWS_DEFAULT_REGION := $(shell aws configure get region)
include ../.env
export

.PHONY: build container run

build:
	rm -rf proxy
	GOOS=linux GOARCH=amd64 go build -o ./proxy .

container:
	docker build --tag eksboot:latest .

run:
	docker run	--name eksboot \
				--rm \
				--detach \
				--publish 8080:8080 \
				--env EKSPHEMERAL_HOME=/eksp \
				--env EKSBOOT_URL=http://localhost \
				--env EKSBOOT_BUCKET=${EKSBOOT_BUCKET} \
				eksboot:latest

verify:
	@docker images quay.io/mhausenblas/eksp-ui:$(ui_version)

stop:
	docker kill eksboot

retry: stop build container run

