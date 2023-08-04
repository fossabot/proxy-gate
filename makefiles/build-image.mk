build-image-test:
	@echo "Building the Docker image (test)..."
	docker build -t $(DOCKER_IMAGE_URL)-test:$(BUILD_VERSION) -f Dockerfile.testenv .

build-image-app:
	@echo "Building the Docker image (app)..."
	docker build -t $(DOCKER_IMAGE_URL):$(BUILD_VERSION) .