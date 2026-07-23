import os
import logging
import urllib.parse
import functools

import sanic
import aiohttp
import orjson
import babel.numbers
import babel.dates
import babel.lists
from npf_renderer import VERSION as NPF_RENDERER_VERSION

from . import routes, hyperblur_extractor, preferences, i18n
from .config import load_config
from .exceptions import error_handlers
from .helpers import helpers, render, ext_npf_renderer


# Load configuration file

config = load_config(os.environ.get("HYPERBLUR_CONFIG_LOCATION", "./config.toml"))

app = sanic.Sanic(
    "Hyperblur",
    loads=orjson.loads,
    dumps=orjson.dumps,
    env_prefix="HYPERBLUR_",
)
app.config.OAS = False

app.ctx.LANGUAGES = i18n.initialize_locales()
app.ctx.SUPPORTED_LANGUAGES = i18n.SUPPORTED_LANGUAGES

# Constants

app.config.TEMPLATING_PATH_TO_TEMPLATES = "src/templates"

app.ctx.NPF_RENDERER_VERSION = NPF_RENDERER_VERSION

app.ctx.URL_HANDLER = helpers.url_handler
app.ctx.BLACKLIST_RESPONSE_HEADERS = ("access-control-allow-origin", "alt-svc", "server")

app.ctx.HYPERBLUR_CONFIG = config
app.ctx.translate = i18n.translate
app.ctx.CURRENT_COMMIT = "1.0.0"

app.ctx.HYPERBLUR_PARENT_DIR_PATH = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
app.ctx.create_user_friendly_error_message = error_handlers.create_user_friendly_error_message


@app.listener("before_server_start")
async def initialize(app):
    hyperblur_backend = app.ctx.HYPERBLUR_CONFIG.backend

    app.ctx.TumblrAPI = await hyperblur_extractor.TumblrAPI.create(
        main_request_timeout=hyperblur_backend.main_response_timeout, json_loads=orjson.loads
    )

    media_request_headers = {
        "user-agent": hyperblur_extractor.TumblrAPI.DEFAULT_HEADERS["user-agent"],
        "accept-encoding": "gzip, deflate",
        "accept": "image/avif,image/webp,image/png,image/svg+xml,image/*;q=0.8,*/*;q=0.5",
        "accept-language": "en-US,en;q=0.5",
        "connection": "keep-alive",
        "te": "trailers",
        "referer": "https://www.tumblr.com/",
    }

    media_connector = aiohttp.TCPConnector(use_dns_cache=True, ttl_dns_cache=600, limit=300, limit_per_host=100, enable_cleanup_closed=True)
    app.ctx.MediaClient = aiohttp.ClientSession(
        headers=media_request_headers,
        timeout=aiohttp.ClientTimeout(hyperblur_backend.image_response_timeout),
        connector=media_connector,
    )

    at_connector = aiohttp.TCPConnector(use_dns_cache=True, ttl_dns_cache=600, limit=300, limit_per_host=100, enable_cleanup_closed=True)
    app.ctx.TumblrAtClient = aiohttp.ClientSession(
        "https://at.tumblr.com",
        headers={"user-agent": hyperblur_extractor.TumblrAPI.DEFAULT_HEADERS["user-agent"]},
        timeout=aiohttp.ClientTimeout(hyperblur_backend.main_response_timeout),
        connector=at_connector,
    )

    # Caching disabled (Redis removed)
    app.ctx.CacheDb = None

    app.ctx.render = render.render_template

    # Add additional jinja filters and functions

    app.ext.environment.add_extension("jinja2.ext.do")

    app.ext.environment.filters["encodepathsegment"] = functools.partial(
        urllib.parse.quote, safe=""
    )

    app.ext.environment.filters["update_query_params"] = helpers.update_query_params
    app.ext.environment.filters["remove_query_params"] = helpers.remove_query_params
    app.ext.environment.filters["deseq_urlencode"] = helpers.deseq_urlencode
    app.ext.environment.filters["ensure_single_prefix_slash"] = (
        helpers.prefix_slash_in_url_if_missing
    )

    app.ext.environment.filters["format_decimal"] = babel.numbers.format_decimal
    app.ext.environment.filters["format_date"] = babel.dates.format_date
    app.ext.environment.filters["format_datetime"] = babel.dates.format_datetime

    app.ext.environment.filters["format_list"] = babel.lists.format_list

    app.ext.environment.globals["translate"] = i18n.translate
    app.ext.environment.globals["url_handler"] = helpers.url_handler
    app.ext.environment.globals["format_npf"] = ext_npf_renderer.format_npf
    app.ext.environment.globals["create_poll_callback"] = helpers.create_poll_callback
    app.ext.environment.globals["create_reblog_attribution"] = (
        helpers.create_reblog_attribution_link
    )

    app.ext.environment.tests["a_post"] = lambda element: isinstance(
        element, hyperblur_extractor.models.post.Post
    )


@app.listener("main_process_start")
async def main_startup_listener(app):
    """Startup listener to notify of hyperblur startup"""
    print("Starting up Hyperblur")


@app.listener("after_server_stop")
async def cleanup(app, loop):
    """Cleanup listener to close all ClientSessions"""
    await app.ctx.MediaClient.close()
    await app.ctx.TumblrAtClient.close()
    await app.ctx.TumblrAPI.client.close()


@app.get("/")
async def root(request):
    return sanic.redirect(request.app.url_for("explore._trending"))


@app.route("/robots.txt")
async def robotstxt_route(request):
    return await sanic.file("./assets/robots.txt")


@app.middleware("request", priority=1)
async def before_all_routes(request):
    request.ctx.preferences = preferences.UserPreferences(
        **config.default_user_preferences._asdict()
    )

    request.ctx.language = request.ctx.preferences.language

    request.ctx.preferences = request.ctx.preferences.replace_from_cookie(request)


@app.middleware("response")
async def after_all_routes(request, response):
    # https://github.com/iv-org/invidious/blob/master/src/invidious/routes/before_all.cr
    response.headers["x-xss-protection"] = "1; mode=block"
    response.headers["x-content-type-options"] = "nosniff"
    response.headers["referrer-policy"] = "same-origin"

    response.headers["content-security-policy"] = "; ".join(
        [
            "default-src 'none'",
            "script-src 'self'",
            "style-src 'self' 'unsafe-inline'",
            "img-src 'self' data:",
            "font-src 'self' data:",
            "connect-src 'self'",
            "manifest-src 'self'",
            "media-src 'self'",
            "child-src 'self' blob:",
        ]
    )


# Register all routes:
for route in routes.BLUEPRINTS:
    app.blueprint(route)

# Register error handlers into Hyperblur
error_handlers.register(app)

if __name__ == "__main__":
    import logging
    logging.basicConfig(level=logging.WARNING)
    logging.getLogger("sanic.access").setLevel(logging.WARNING)

    app.run(
        host=config.deployment.host,
        port=config.deployment.port,
        workers=config.deployment.workers,
        dev=config.misc.dev_mode,
        access_log=False,
    )
