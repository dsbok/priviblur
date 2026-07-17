import urllib.parse

import sanic
from src.exceptions import exceptions

miscellaneous = sanic.Blueprint("miscellaneous", url_prefix="/")


@miscellaneous.get(r"/at/<path:path>")
async def _at_links(request: sanic.Request, path: str):
    """Redirects for at.tumblr.com links"""
    response = await request.app.ctx.TumblrAtClient.head(f"/{path}")

    if response.status == 301:
        location = urllib.parse.urlparse(response.headers["location"])
        if location.path.startswith("/"):
            return sanic.redirect(location.path)

    raise exceptions.TumblrInvalidRedirect()


@miscellaneous.get(r"/post/<post_id:int>")
async def _post_lookup(request: sanic.Request, post_id: int):
    """Direct post lookup by post ID"""
    url = f"https://www.tumblr.com/post/{post_id}"
    try:
        async with request.app.ctx.MediaClient.head(url, allow_redirects=False) as response:
            if response.status in (301, 302, 307, 308) and "location" in response.headers:
                location_url = response.headers["location"]
                parsed = urllib.parse.urlparse(location_url)
                host = parsed.netloc.lower()
                path = parsed.path.strip("/")
                parts = path.split("/")
                
                blog = None
                if host.endswith(".tumblr.com") and host != "www.tumblr.com":
                    blog = host.split(".")[0]
                elif host == "www.tumblr.com" and len(parts) >= 2:
                    blog = parts[0]
                
                if blog:
                    slug = parts[2] if len(parts) >= 3 else None
                    if slug:
                        return sanic.redirect(f"/{blog}/{post_id}/{slug}")
                    return sanic.redirect(f"/{blog}/{post_id}")
    except Exception:
        pass
        
    raise exceptions.TumblrInvalidRedirect()
