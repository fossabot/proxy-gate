.PHONY : local-run

local-run: build
	@echo "Running the Docker compose up..."
	docker compose --file examples/docker-compose.yaml up --detach --force-recreate
