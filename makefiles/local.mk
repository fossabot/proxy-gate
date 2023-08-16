.PHONY : local-run

local-run: build
ifndef NGROK_AUTHTOKEN
	$(error NGROK_AUTHTOKEN is not defined. Please set it before running this command.)
endif
	@echo "Running the Docker compose up..."
	docker compose --file examples/docker-compose.yaml up --detach

docker-clean:
	@echo "Running docker clean..."
	docker compose --file examples/docker-compose.yaml down
	docker system prune --all --force
