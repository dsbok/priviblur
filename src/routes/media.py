import sanic
import aiohttp
import asyncio

from src.exceptions import exceptions

media = sanic.Blueprint("TumblrMedia", url_prefix="/tblr")


async def get_media(
    request, client: aiohttp.ClientSession, path_to_request, additional_headers=None, base_url=""
):
    url = f"{base_url}/{path_to_request}"
    try:
        async with client.get(url, headers=additional_headers) as tumblr_response:
            priviblur_response_headers = {}
            for header_key, header_value in tumblr_response.headers.items():
                if header_key.lower() not in request.app.ctx.BLACKLIST_RESPONSE_HEADERS:
                    priviblur_response_headers[header_key] = header_value

            if tumblr_response.status == 200:
                priviblur_response_headers["Cache-Control"] = "public, max-age=31536000, immutable"
            elif tumblr_response.status == 301:
                if location := priviblur_response_headers.get("location"):
                    location = request.app.ctx.URL_HANDLER(location)
                    if not location.startswith("/"):
                        raise exceptions.TumblrInvalidRedirect()

                    return sanic.redirect(location)
            elif tumblr_response.status in (429, 500, 502, 503, 504):
                return sanic.response.empty(status=502)

            priviblur_response = await request.respond(headers=priviblur_response_headers, status=tumblr_response.status)

            try:
                async for chunk in tumblr_response.content.iter_chunked(65536):
                    await priviblur_response.send(chunk)
            except (asyncio.CancelledError, ConnectionResetError):
                pass
            finally:
                await priviblur_response.eof()

    except (aiohttp.ClientError, asyncio.TimeoutError):
        return sanic.response.empty(status=504)
    except exceptions.TumblrInvalidRedirect:
        raise
    except Exception:
        return sanic.response.empty(status=502)


@media.get("/media/<cdn:str>/<path:path>")
async def _media_cdn(request: sanic.Request, cdn: str, path: str):
    """Proxies media from *.media.tumblr.com"""
    client = request.app.ctx.MediaClient
    base_url = f"https://{cdn}.media.tumblr.com"
    additional_headers = None
    if cdn in ("ve", "va"):
        additional_headers = {
            "accept": "video/webm,video/ogg,video/*;q=0.9, application/ogg;q=0.7,audio/*;q=0.6,*/*;q=0.5"
        }
    return await get_media(request, client, path, additional_headers=additional_headers, base_url=base_url)


@media.get(r"/a/<path:path>")
async def _a_media(request: sanic.Request, path: str):
    """Proxies the requested media from a.tumblr.com"""
    additional_headers = {
        "accept": "audio/webm,audio/ogg,audio/wav,audio/*;q=0.9,application/ogg;q=0.7,video/*;q=0.6,*/*;q=0.5"
    }
    return await get_media(
        request, request.app.ctx.MediaClient, path, additional_headers=additional_headers, base_url="https://a.tumblr.com"
    )


@media.get(r"/assets/<path:path>")
async def _tb_assets(request: sanic.Request, path: str):
    """Proxies the requested media from assets.tumblr.com"""
    return await get_media(request, request.app.ctx.MediaClient, path, base_url="https://assets.tumblr.com")


@media.get(r"/static/<path:path>")
async def _tb_static(request: sanic.Request, path: str):
    """Proxies the requested media from static.tumblr.com"""
    return await get_media(request, request.app.ctx.MediaClient, path, base_url="https://static.tumblr.com")

