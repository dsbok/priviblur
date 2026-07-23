# Hyperblur

Hyperblur is a ultra-fast, privacy-focused, lightweight alternative frontend for Tumblr. Built for maximum speed, security, and anonymity, it lets you browse Tumblr content without tracking, without an account, and with zero external CDNs or heavy frameworks.

## Core Highlights & Features

- **Ultra-Fast Performance**: Zero external CDNs or frameworks. Pure HTML, CSS, and vanilla AJAX (`fetch()`). Native browser rendering acceleration (`content-visibility: auto`, system fonts).
- **Sharp Minimalist Dark Theme**: Dark grey canvas (`#1e1e1e`), sharp contrast `#ffffff` text, clean sharp borders (`0px` rounded corners), and crisp blue hyperlinks (`#3399ff`).
- **Privacy & Anonymity**: All media proxies, API calls, and asset requests go through your backend container. Tumblr never receives direct user traffic or client IP addresses.
- **Embedded Source Locales**: Language strings are directly embedded inside `src/i18n/translations.py` for zero runtime disk/compilation overhead.
- **One-Click Video Downloads**: Download videos directly from any post with a built-in download action button.
- **Full Fallback Support**: Fully functional without JavaScript enabled. View blogs, read post notes, perform searches, and browse trending feeds seamless with pure HTML.

---

## Quick Start (Docker)

### 1. Launch with Docker Compose
Run Hyperblur locally on port **8010**:

```bash
docker compose up -d --build
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
docker build -t hyperblur:latest -f docker/Dockerfile .

# Run container on port 8010
docker run -d \
  --name hyperblur \
  -p 8010:8000 \
  -e HYPERBLUR_DEPLOYMENT_HOST=0.0.0.0 \
  -e HYPERBLUR_DEPLOYMENT_PORT=8000 \
  -e HYPERBLUR_DEPLOYMENT_WORKERS=4 \
  hyperblur:latest
```

---

## Environment Configuration

All application configuration parameters can be passed via environment variables in `docker-compose.yml` or container launch commands:

| Variable | Default | Description |
| :--- | :--- | :--- |
| `HYPERBLUR_DEPLOYMENT_HOST` | `0.0.0.0` | IP address the Sanic web server binds to inside container |
| `HYPERBLUR_DEPLOYMENT_PORT` | `8000` | Internal container TCP port |
| `HYPERBLUR_DEPLOYMENT_HTTPS` | `true` | Enables secure cookie flags and HTTPS header policies |
| `HYPERBLUR_DEPLOYMENT_WORKERS` | `4` | Number of concurrent web server worker processes |
| `HYPERBLUR_TUMBLR_AUTHORIZATION` | *(Optional)* | Tumblr OAuth / Bearer token to access private or log-in restricted blogs |

---

## Security & Container Hardening

- **Base Image**: Python 3.13 Alpine (`python:3.13-alpine`), updated with zero CVE vulnerability findings.
- **Non-Root Execution**: Runs as non-privileged user `hyperblur` (UID 1000).
- **Process Supervisor**: Managed by `/sbin/tini` for signal handling and zombie process reaping.
- **Strict Headers**: Enforces Security Headers (`Content-Security-Policy`, `X-Content-Type-Options: nosniff`, `X-XSS-Protection`).

---

## License

Distributed under the [GNU AGPLv3 License](LICENSE).
