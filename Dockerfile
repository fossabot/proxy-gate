ARG APP_VERSION=0.0.0
ARG FROM_IMAGE=python:3.9
ARG IMAGE_REVISION=""
ARG IMAGE_REF_NAME=""
FROM $FROM_IMAGE

LABEL org.opencontainers.image.authors="hey@digimach.com" \
    org.opencontainers.image.base.digest="" \
    org.opencontainers.image.base.name="$FROM_IMAGE" \
    org.opencontainers.image.created="" \
    org.opencontainers.image.description="Proxy Gate" \
    org.opencontainers.image.documentation="" \
    org.opencontainers.image.licenses="BSD-3-Clause" \
    org.opencontainers.image.ref.name="$IMAGE_REF_NAME" \
    org.opencontainers.image.revision="$IMAGE_REVISION" \
    org.opencontainers.image.source="https://github.com/digimach/proxy-gate" \
    org.opencontainers.image.source="" \
    org.opencontainers.image.title="proxy-gate" \
    org.opencontainers.image.url="" \
    org.opencontainers.image.vendor="Digimach" \
    org.opencontainers.image.version=$APP_VERSION

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file to the container
COPY requirements.txt .

# Install the Python dependencies
RUN pip install --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# Copy the app source
COPY . .

# Run the Flask application
CMD [ "./start.sh" ]
