# Hyperblur

Hyperblur is a ultra-fast, privacy-focused, lightweight alternative frontend for Tumblr. Built for maximum speed, security, and anonymity, it lets you browse Tumblr content without tracking and without an account. Hyperblur is a fork of https://github.com/syeopite/priviblur but with improvements.

## Core Highlights & Features

- **Ultra-Fast Performance**: Zero external CDNs or frameworks. Pure HTML, CSS, and vanilla AJAX.
- **Privacy & Anonymity**: All media proxies, API calls, and asset requests go through your backend container. Tumblr never receives direct user traffic or client IP addresses.
- **One-Click Video Downloads**: Download videos directly from any post with a built-in download action button.
- **Full Fallback Support**: Fully functional without JavaScript enabled. View blogs, read post notes, perform searches, and browse trending feeds seamless with pure HTML.

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
