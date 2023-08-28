include makefiles/*.mk
.PHONY: pytest build push clean integration-test 

pytest: build-image-test
	@echo "Running tests..."
	$(eval TEMP_FILE := $(shell mktemp))
	env > $(TEMP_FILE)
	docker run --interactive --env-file $(TEMP_FILE) --user $$(id --user) --workdir /app  -v $$(pwd):/app $(DOCKER_IMAGE_URL)-test:$(BUILD_VERSION) pytest -vvvv --strict-markers --basetemp=./.pytest_tmp/ --cov-report term-missing --cov=. --cov-fail-under=69.81 --cov-report xml:coverage.xml --cov-report=html

build: build-image-app build-image-test
push: build
	@echo "Pushing the Docker image to container registry..."
	docker push $(DOCKER_IMAGE_URL):$(BUILD_VERSION)

clean: docker-clean
	@echo "Cleaning up..."
	git clean -d --force -X

integration-test: local-run
	@echo "Running integration tests..."
	sleep 20s
	curl -i -k --resolve auth.localhost:443:127.0.0.1 https://auth.localhost/healthz
