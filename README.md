# Hyperblur

Hyperblur is a ultra-fast, privacy-focused, lightweight alternative frontend for Tumblr. Built for maximum speed, security, and anonymity, it lets you browse Tumblr content without tracking and without an account. Hyperblur is a fork of https://github.com/syeopite/priviblur but with improvements.

## Features

- **Blazing Fast**: Eager media loading, background next-page prefetching, and unbounded proxy streaming for an instant browsing experience.
- **Private by Default**: All API and media requests are reverse-proxied. Tumblr never sees your client IP.
- **Lightweight**: Zero external CDNs or heavy JS frameworks. Works flawlessly with JavaScript disabled.
- **Enhanced UX**: Built-in one-click video downloads and highly responsive feeds.

## Technologies Used

- **Sanic & uvloop**: High-performance asynchronous web server powering the backend.
- **aiohttp**: Drives concurrent, zero-buffer proxying for raw media streams.
- **Python 3.13 JIT**: Utilizes the experimental Tier 2 optimizer for maximum server execution speed.
- **Jinja2**: Fast, server-side template rendering for minimal client-side overhead.

---

## Quick Start (Docker)

### 1. Launch with Docker Compose
Create a `docker-compose.yml` file with the following configuration:

```yaml
services:
  hyperblur:
    image: ghcr.io/dsbok/hyperblur:main
    container_name: hyperblur
    restart: unless-stopped
    ports:
      - "0.0.0.0:8010:8000"
    environment:
      # Uncomment to allow viewing blogs that require being logged in
      # - HYPERBLUR_TUMBLR_AUTHORIZATION=Bearer YOUR_TOKEN_HERE

```

Run Hyperblur locally on port **8010**:

```bash
docker compose up -d

```

Access the interface in your browser at:
**`http://localhost:8010`**

### 2. Stop the Application

```bash
docker compose down -v

```

---

## Manual Docker Build & Deployment

If you prefer building and running the container manually with Docker commands:

```bash
# Build the production Docker image
docker build -t hyperblur:latest -f Dockerfile .

# Run container on port 8010
docker run -d \
  --name hyperblur \
  -p 8010:8000 \
  hyperblur:latest

```

---

## Environment Configuration

All application configuration parameters can be passed via environment variables in `docker-compose.yml` or container launch commands:

| Variable | Default | Description |
| --- | --- | --- |
| `HYPERBLUR_TUMBLR_AUTHORIZATION` | *(Optional)* | Tumblr OAuth / Bearer token to access private or log-in restricted blogs |

---

## License

Distributed under the [GNU AGPLv3 License](https://www.google.com/search?q=LICENSE).
