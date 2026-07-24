# Hyperblur

A fast, minimalist web interface for Tumblr.

## Features

- High performance and raw throughput
- Dark theme
- "Media Only" filter to hide text posts
- Numbered pagination to easily skip pages
- Extracted blog metadata details (UUID, theme info, post counts)
- Native video downloading

## Usage

1. Start the container with Docker Compose (automatically uses the latest pre-built `ghcr.io` image):
   ```bash
   docker compose up -d
   ```

2. Open `http://localhost:8010/` in your browser.
