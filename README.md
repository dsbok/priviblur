# Hyperblur

An ultra-fast, privacy-focused, and lightweight alternative frontend for Tumblr. Hyperblur proxies all media and API requests, ensuring tracking-free and account-free browsing. (Forked from [Priviblur](https://github.com/syeopite/priviblur)).

### Tech Stack
Built for raw speed using **Sanic**, **aiohttp**, **Jinja2**, and **Python 3.13 JIT**. Features unbounded zero-buffer media proxying and eager data fetching.

### Quick Start (Docker)

```yaml
# docker-compose.yml
services:
  hyperblur:
    image: ghcr.io/dsbok/hyperblur:main
    ports:
      - "8010:8000"
    # environment:
    #   HYPERBLUR_TUMBLR_AUTHORIZATION: Bearer <TOKEN>
```

```bash
docker compose up -d
```

Access at `http://localhost:8010`.

---
Distributed under the [GNU AGPLv3 License](https://www.google.com/search?q=LICENSE).
