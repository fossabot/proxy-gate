import multiprocessing

bind = "0.0.0.0:5000"  # The address and port to bind the server
workers = multiprocessing.cpu_count() * 2 + 1  # Number of worker processes
threads = 2  # Number of threads per worker process
worker_class = "gthread"  # Worker class for handling requests
timeout = 60  # Request timeout in seconds
keepalive = 5  # Keep-alive connection timeout in seconds

# Logging configuration
accesslog = "-"  # Access log file, use '-' for stdout
errorlog = "-"  # Error log file, use '-' for stdout
loglevel = "info"  # Log level: debug, info, warning, error, critical

# SSL/TLS configuration (uncomment and configure if using HTTPS)
# keyfile = "/path/to/private_key.pem"
# certfile = "/path/to/certificate.pem"

# Application-specific configuration
# You can add additional configuration options specific to your Flask app here
# For example:
# env = "MYAPP_SETTINGS=production"
# raw_env = ["FLASK_APP=wsgi:app", "FLASK_ENV=production"]
