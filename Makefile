include makefiles/*.mk
.PHONY: test build push run 

test: build-image-test
	@echo "Running tests..."
	$(eval TEMP_FILE := $(shell mktemp))
	env > $(TEMP_FILE)
	docker run -ti --env-file $(TEMP_FILE) --user $$(id --user) --workdir /app  -v $$(pwd):/app $(DOCKER_IMAGE_URL)-test:$(BUILD_VERSION) pytest -vvvv --strict-markers --basetemp=./.pytest_tmp/ --cov-report term-missing --cov=. --cov-fail-under=100 --cov-report=html

build: build-image-app build-image-test
push: build
	@echo "Pushing the Docker image to container registry..."
	echo $$GITHUB_TOKEN | docker login $(DOCKER_REPO) --username USERNAME --password-stdin
	docker push $(DOCKER_IMAGE_URL):$(BUILD_VERSION)

clean: docker-clean
	@echo "Cleaning up..."
	git clean -d --force -X
