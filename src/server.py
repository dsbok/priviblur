import os
import logging
import urllib.parse
import functools

import sanic
import aiohttp
import orjson
from npf_renderer import VERSION as NPF_RENDERER_VERSION

from . import routes, hyperblur_extractor, helpers, exceptions
from .config import load_config


ENGLISH_STRINGS = {
    "project_title": "Hyperblur",
    "page_title_suffix": "- Hyperblur",
    "post_note_count": "{0} notes",
    "search_bar_placeholder_text": "Search",
    "navbar_today_on_tumblr_icon_title": "Today on Tumblr",
    "navbar_trending_icon_title": "Trending",
    "navbar_right_view_page_on_tumblr_link_title": "View page on Tumblr",
    "navbar_right_settings_page_title": "Settings",
    "footer_version_text": "Version {0}",
    "footer_source_link_text": "Source",
    "footer_donate_link_text": "Donate",
    "footer_licences_link_text": "Licences",
    "dropdown_filter_menu_text": "Filter",
    "timeline_search_sort_by_filter_title": "Sort by",
    "timeline_search_sort_by_filter_popular": "Popular",
    "timeline_search_sort_by_filter_recent": "Latest",
    "timeline_search_filter_by_date_filter_title": "Filter by date",
    "timeline_search_filter_by_date_filter_0": "All Time",
    "timeline_search_filter_by_date_filter_1": "Today",
    "timeline_search_filter_by_date_filter_7": "Last week",
    "timeline_search_filter_by_date_filter_30": "Last month",
    "timeline_search_filter_by_date_filter_180": "Last 6 months",
    "timeline_search_filter_by_date_filter_365": "Last year",
    "timeline_search_post_type_filter_none": "All Types",
    "timeline_search_post_type_filter_title": "Filter by post type",
    "timeline_search_post_type_filter_text": "Text",
    "timeline_search_post_type_filter_photo": "Photo",
    "timeline_search_post_type_filter_gif": "Gifs",
    "timeline_search_post_type_filter_quote": "Quote",
    "timeline_search_post_type_filter_link": "Link",
    "timeline_search_post_type_filter_chat": "Chat",
    "timeline_search_post_type_filter_audio": "Audio",
    "timeline_search_post_type_filter_video": "Video",
    "timeline_search_post_type_filter_ask": "Ask",
    "timeline_search_post_type_filter_poll": "Poll",
    "timeline_tagged_sort_by_filter_title": "Sort by",
    "timeline_tagged_sort_by_filter_top": "Top",
    "timeline_tagged_sort_by_filter_recent": "Latest",
    "explore_trending_page_title": "Trending topics",
    "explore_today_on_tumblr_page_title": "Today on Tumblr",
    "pagination_next_page": "Next page",
    "tumblr_error_blog_login_required_error_heading": "This blog requires an account to view",
    "tumblr_error_blog_login_required_error_description": "Try finding reblogs instead!",
    "tumblr_error_restricted_tag_error_heading": "This tag has been restricted on Tumblr",
    "tumblr_error_restricted_tag_description": "Try performing a search instead",
    "tumblr_error_blog_not_found_error_heading": "Unable to find the requested blog",
    "tumblr_error_blog_not_found_error_description": "The blog may have been deleted or just never existed in the first place",
    "tumblr_error_blog_requires_password_error_heading": "This blog requires a password to access",
    "tumblr_error_ratelimit_reached_heading": "Hyperblur has been ratelimited by Tumblr",
    "tumblr_error_ratelimit_reached_description": "Please try again later",
    "hyperblur_error_page_title": "Error",
    "hyperblur_error_request_to_tumblr_timed_out_heading": "Error: Request to Tumblr timed out",
    "hyperblur_error_request_to_tumblr_timed_out_description": "Hyperblur was unable to complete the request to Tumblr before timing out",
    "hyperblur_error_invalid_internal_tumblr_redirect": "Error: Tumblr HTTP 301 redirect points to foreign URL",
    "hyperblur_error_generic": "An unknown exception has occured!",
    "hyperblur_error_generic_description": "It looks like you have found a bug in Hyperblur.",
    "hyperblur_error_generic_description_2": "Please report it here at GitHub",
    "hyperblur_error_generic_technical_details_expansion_box_label": "Show error log",
    "post_community_label_mature_heading": "Community Label: Mature",
    "post_community_label_generic_explanation": "This post may contain content that is not suitable for all audiences.",
    "post_community_label_sexual_themes": "Sexual themes",
    "post_community_label_drug_use": "Drug and alcohol addiction",
    "post_community_label_violence": "Violence",
    "post_community_label_show_post_button": "Show post",
    "post_community_label_no_js_show_post_instructions": "Reveals on hover",
    "post_footer_permalink_icon_title": "Permalink",
    "post_footer_view_on_tumblr_icon_title": "View on Tumblr",
    "blog_search_placeholder_text": "Search posts",
    "blog_banner_alt": "Blog banner",
    "blog_avatar_alt": "Blog avatar",
    "settings_header": "Settings",
    "settings_language_selector": "Language",
    "settings_language_selector_desc": "Select which language you'd like Hyperblur to use",
    "hyperblur_licences_page_title": "Licences",
    "post_note_viewer_view_replies_tab_title": "Replies",
    "post_note_viewer_view_reblogs_tab_title": "Reblogs",
    "post_note_viewer_view_likes_tab_title": "Likes",
    "post_note_viewer_view_reblogs_filter_reblogs_with_comments": "Comments and tags",
    "post_note_viewer_view_reblogs_filter_reblogs_with_content_comments": "Comments only",
    "post_note_viewer_view_reblogs_filter_reblogs_only": "Other reblogs",
    "post_note_viewer_view_replies_filter_sort_oldest": "Oldest first",
    "post_note_viewer_view_replies_filter_sort_newest": "Newest first",
    "npf_renderer_asker_with_no_attribution": "Anonymous",
    "npf_renderer_asker_and_ask_verb": "{name} asked",
    "npf_renderer_unsupported_block_header": "Unsupported NPF block",
    "npf_renderer_unsupported_block_description": "Placeholder for the unsupported \"{block}\" type NPF block",
    "npf_renderer_generic_image_alt_text": "image",
    "npf_renderer_link_block_poster_alt_text": "Preview image for \"{site}\"",
    "npf_renderer_link_block_fallback_embeds_are_disabled": "Embeds are disabled",
    "npf_renderer_error_video_link_block_fallback_heading": "Error: unable to render video block",
    "npf_renderer_video_link_block_fallback_description": "Please click me to watch on the original site",
    "npf_renderer_error_video_link_block_fallback_heading": "Error: unable to render video block",
    "npf_renderer_fallback_audio_block_thumbnail_alt_text": "Album art",
    "npf_renderer_error_audio_link_block_fallback_heading": "Error: unable to render audio block",
    "npf_renderer_audio_link_block_fallback_description": "Please click me to listen on the original site",
    "npf_renderer_poll_total_votes": "{votes} votes",
    "npf_renderer_poll_remaining_time": "{duration} remaining",
    "npf_renderer_poll_ended_on": "Ended on: {ended_date}",
    "npf_renderer_post_attribution": "From {author}",
    "npf_renderer_blog_attribution": "Created by {author}",
    "npf_renderer_app_attribution": "View on {platform}",
    "npf_renderer_unsupported_attribution": "Attributed via an unsupported attribution type.",
    "alert_partial_restricted_results_heading": "Quick Update on Your Search Results",
    "alert_partial_restricted_results_message": "These search results have been partially restricted due to Tumblr's content guidelines. You can expect to see some empty results here sporadically.",
    "alert_restricted_results_heading": "Restricted search results",
    "alert_restricted_results_message": "These search results have been blocked by Tumblr for violating their content guidelines.",
    "alert_view_post_on_account_restricted_blog_heading": "This blog requires an account to view",
    "alert_view_post_on_account_restricted_blog_message": "Only individual posts like this one can be displayed",
    "alert_error_on_rendering_post_contents_heading": "Failed to render the contents of this post",
    "alert_error_on_rendering_post_contents": "The contents of this post has failed to render due to an error. Check below for more information",
}

def translate_english(lang, key, number=None, substitution=None):
    val = ENGLISH_STRINGS.get(key, key)
    if isinstance(val, (list, tuple)):
        idx = 0 if (number == 1 or number == 1.0) else 1
        val = val[idx] if len(val) > idx else val[0]
    if isinstance(substitution, str):
        return val.format(substitution)
    elif isinstance(substitution, dict):
        return val.format(**substitution)
    elif number is not None and "{0}" in val:
        return val.format(number)
    return str(val)

config = load_config(os.environ.get("HYPERBLUR_CONFIG_LOCATION", "./config.toml"))

app = sanic.Sanic(
    "Hyperblur",
    loads=orjson.loads,
    dumps=orjson.dumps,
    env_prefix="HYPERBLUR_",
)
app.config.OAS = False

app.ctx.LANGUAGES = {"en_US": type("Lang", (), {"name": "English"})()}
app.ctx.SUPPORTED_LANGUAGES = ["en_US"]

app.config.TEMPLATING_PATH_TO_TEMPLATES = "src/templates"
app.ctx.NPF_RENDERER_VERSION = NPF_RENDERER_VERSION
app.ctx.URL_HANDLER = helpers.url_handler
app.ctx.BLACKLIST_RESPONSE_HEADERS = frozenset({"access-control-allow-origin", "alt-svc", "server"})

STATIC_CSP_HEADER = "default-src 'none'; script-src 'self'; style-src 'self' 'unsafe-inline'; img-src 'self' data:; font-src 'self' data:; connect-src 'self'; manifest-src 'self'; media-src 'self'; child-src 'self' blob:"

app.ctx.HYPERBLUR_CONFIG = config
app.ctx.CURRENT_COMMIT = "1.0.0"
app.ctx.HYPERBLUR_PARENT_DIR_PATH = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
app.ctx.create_user_friendly_error_message = exceptions.create_user_friendly_error_message


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

    media_connector = aiohttp.TCPConnector(use_dns_cache=True, ttl_dns_cache=600, limit=0, limit_per_host=0, enable_cleanup_closed=True)
    app.ctx.MediaClient = aiohttp.ClientSession(
        headers=media_request_headers,
        timeout=aiohttp.ClientTimeout(hyperblur_backend.image_response_timeout),
        connector=media_connector,
        auto_decompress=False,
    )

    at_connector = aiohttp.TCPConnector(use_dns_cache=True, ttl_dns_cache=600, limit=0, limit_per_host=0, enable_cleanup_closed=True)
    app.ctx.TumblrAtClient = aiohttp.ClientSession(
        "https://at.tumblr.com",
        headers={"user-agent": hyperblur_extractor.TumblrAPI.DEFAULT_HEADERS["user-agent"]},
        timeout=aiohttp.ClientTimeout(hyperblur_backend.main_response_timeout),
        connector=at_connector,
    )

    app.ctx.CacheDb = None
    app.ctx.render = helpers.render_template

    app.ext.environment.add_extension("jinja2.ext.do")
    app.ext.environment.filters["encodepathsegment"] = functools.partial(urllib.parse.quote, safe="")
    app.ext.environment.filters["update_query_params"] = helpers.update_query_params
    app.ext.environment.filters["remove_query_params"] = helpers.remove_query_params
    app.ext.environment.filters["deseq_urlencode"] = helpers.deseq_urlencode
    app.ext.environment.filters["ensure_single_prefix_slash"] = helpers.prefix_slash_in_url_if_missing
    app.ext.environment.filters["format_decimal"] = lambda x, **kw: f"{x:,}"
    app.ext.environment.filters["format_date"] = lambda d, **kw: d.strftime("%b %d, %Y")
    app.ext.environment.filters["format_datetime"] = lambda d, **kw: d.strftime("%b %d, %Y %H:%M")
    app.ext.environment.filters["format_list"] = lambda l, **kw: ", ".join(map(str, l))

    app.ext.environment.globals["translate"] = translate_english
    app.ext.environment.globals["url_handler"] = helpers.url_handler
    app.ext.environment.globals["format_npf"] = helpers.format_npf
    app.ext.environment.globals["create_poll_callback"] = helpers.create_poll_callback
    app.ext.environment.globals["create_reblog_attribution"] = helpers.create_reblog_attribution_link
    app.ext.environment.tests["a_post"] = lambda element: isinstance(element, hyperblur_extractor.Post)


@app.listener("main_process_start")
async def main_startup_listener(app):
    print("Starting up Hyperblur")


@app.listener("after_server_stop")
async def cleanup(app, loop):
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
    request.ctx.language = "en_US"


@app.middleware("response")
async def after_all_routes(request, response):
    response.headers["x-xss-protection"] = "1; mode=block"
    response.headers["x-content-type-options"] = "nosniff"
    response.headers["referrer-policy"] = "same-origin"
    response.headers["content-security-policy"] = STATIC_CSP_HEADER


for route in routes.BLUEPRINTS:
    app.blueprint(route)

exceptions.register(app)

if __name__ == "__main__":
    logging.basicConfig(level=logging.WARNING)
    logging.getLogger("sanic.access").setLevel(logging.WARNING)
    app.run(
        host=config.deployment.host,
        port=config.deployment.port,
        dev=config.misc.dev_mode,
        access_log=False,
        fast=True,
    )
