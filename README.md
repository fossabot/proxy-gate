<div align="center">
  <img src="./assets/proxy-gate-logo.svg">
</div>

---

Proxy Gate adds authentication and access controls to apps using Nginx as a proxy frontend. It enables seamless external authentication, allowing you to enhance your apps' security by adding authentication and authorization checks.

## Workflow

![enter image description here](./assets/proxy-gate-high-level-workflow.svg)

## Auhentication and Authorization Workflow

![Auhentication and Authorization Workflow](./assets/proxy-gate-authentication-and-authorization-workflow.svg)

## External Identity Providers

1. Plex
1. Apple (Coming Soon)
1. Facebook (Coming Soon)
1. Google (Coming Soon)
1. LDAP (Coming Soon)

## Authentication

Proxy Gate performs authentication as requested by the Proxy.

## Authorization

### Plex

- Perform check that the user has access to a Plex server before granted access to the resource.
- Provide access based on the user's email address
- The user has Two Factor Enabled on Plex

## Quick Start

Using the [docker compose file](./examples/docker-compose.yaml):

```
docker compose up --detach
```

Nginx should be available at: https://localhost
Demonstration for a Plex Authentication: https://app-behind-plex.localhost

## Configuration

### Flask Configuration

The following methods can be used to configure the Flask instance. They are in order in which they are loaded:
https://flask.palletsprojects.com/en/2.3.x/config/

1. Loaded from the $PROXY_GATE_DATA_DIR/flask-config.yml
1. Set the Flask configuration via environment variable by prefixing the variable name with `FLASK_`

SQL Alchemey Configuration
Same as Flask Configuration

### Gunicorn Configuration

Loaded from $PROXY_GATE_DATA_DIR/gunicorn.conf.py

### Proxy Gate (Coming Soon)

Loaded from $PROXY_GATE_DATA_DIR/proxy-gate-config.py
