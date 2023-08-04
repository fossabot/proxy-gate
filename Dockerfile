FROM python:3.9

LABEL org.opencontainers.image.source https://github.com/digimach/proxy-gate

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
