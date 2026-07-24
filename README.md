# Hyperblur

An ultra-fast, privacy-focused, and lightweight alternative frontend for Tumblr. Hyperblur proxies all media and API requests, ensuring tracking-free and account-free browsing. (Forked from [Priviblur](https://github.com/syeopite/priviblur)).

### Tech Stack
Built for raw speed using **Sanic**, **aiohttp**, **Jinja2**, and **Python 3.13 JIT**. Features unbounded zero-buffer media proxying and eager data fetching.

### Features
- **Total Privacy**: All requests are reverse-proxied; Tumblr never sees your IP or tracks your browsing.
- **Blazing Fast**: Zero-buffer media streaming, background page prefetching, and raw compressed pass-through.
- **JS-Free Fallback**: Browse blogs, notes, and searches flawlessly even with JavaScript disabled.
- **One-Click Downloads**: Save videos locally directly from any post.
- **Advanced Filtering**: Sort searches and timelines by media type, popularity, or recency.


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

### Custom Authorization Token (Optional)
Hyperblur works perfectly out-of-the-box for public Tumblr content without any configuration. However, if you want to view private, age-restricted, or logged-in-only blogs, you can provide your own Tumblr authorization token.

**How to get it:**
1. Log into Tumblr in your browser.
2. Open Developer Tools (F12) and go to the **Network** tab.
3. Refresh the page and click on any API request (like `graphql` or `timeline`).
4. Scroll down to **Request Headers** and copy the entire value of the `Authorization` header (it looks like `Bearer ...`).
5. Uncomment the `HYPERBLUR_TUMBLR_AUTHORIZATION` line in your `docker-compose.yml` and paste the token there.

---
Distributed under the [GNU AGPLv3 License](https://www.google.com/search?q=LICENSE).
