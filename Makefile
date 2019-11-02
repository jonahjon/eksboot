.PHONY: build

build:
	docker-compose up --build

clean:
	docker-compose down
	docker system prune -a
	docker-compose up --build
	