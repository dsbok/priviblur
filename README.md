# Priviblur

Priviblur is an alternative, lightweight, privacy-focused frontend to Tumblr. It proxies requests to Tumblr so you can browse without tracking, has no account requirements, and works without Javascript.

## Features

- Image and video proxying
- Video download button
- Anonymous browsing

## Installation

### Docker

Use the provided `docker-compose.yml` to run the application:

```bash
docker compose up -d
```

### Manual

```bash
git clone "https://github.com/dsbok/priviblur"
cd priviblur
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
pybabel compile -d locales -D priviblur
python -m src.server
```

## Configuration

Configure options by setting environment variables in `docker-compose.yml` or your system environment:

- `PRIVIBLUR_DEPLOYMENT_HOST`: Host to bind to (default: `0.0.0.0`)
- `PRIVIBLUR_DEPLOYMENT_PORT`: Internal port to listen on (default: `8000`), must be same as in docker-compose.yml right port
- `PRIVIBLUR_DEPLOYMENT_DOMAIN`: Domain name of the instance
- `PRIVIBLUR_DEPLOYMENT_HTTPS`: Force HTTPS cookies/links (true/false)
- `PRIVIBLUR_DEPLOYMENT_WORKERS`: Number of worker instances (speedup loading)

## License

AGPLv3
