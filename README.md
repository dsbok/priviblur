# Priviblur

Priviblur is a lightweight, privacy-focused alternative frontend to Tumblr. It allows browsing Tumblr without tracking, without an account, and works without JavaScript.

## 🎨 UI/UX: Minimalist Monochrome Brutalist
- **Geometry**: Symmetrical `2px solid #ffffff` card borders with zero box-shadows.
- **Palette**: Dark scale (`#0e0e10` backdrop, `#16161a` cards, `#ffffff` highlights).
- **Typography**: System monospace stack (`"SF Mono"`, `"Fira Code"`, etc.).
- **Interactions**: Flat buttons with monochrome hover states (white/gray inversion).

## 🚀 Core Features
- **Privacy Proxying**: All requests (media/data) are proxied through the server.
- **Account-Free**: View public blogs, trending feeds, and search anonymously.
- **JS-Free Fallback**: Browse, read post notes, and search with client-side JavaScript disabled.
- **Vulnerability Compliance**: Optimized Docker container with zero runtime Git dependencies, verified clean via Trivy and Grype.

## 🛠️ Getting Started (Docker Only)

### 1. Start the Application
```bash
docker compose up -d
```
The application will be available at `http://localhost:8009`.

### 2. Stop the Application
```bash
docker compose down -v
```

## ⚙️ Configuration

Essential settings in `docker-compose.yml`:
- `PRIVIBLUR_DEPLOYMENT_HOST`: Deployment host (default: `0.0.0.0`).
- `PRIVIBLUR_DEPLOYMENT_PORT`: Internal container port (default: `8000`).
- `PRIVIBLUR_DEPLOYMENT_HTTPS`: Enables HTTPS secure cookies (default: `true`).
- `PRIVIBLUR_DEPLOYMENT_WORKERS`: Number of web worker processes (default: `4`).
- `PRIVIBLUR_CURRENT_COMMIT`: Version query parameter for asset cache-busting.

## 📄 License
AGPLv3
