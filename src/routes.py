import asyncio
import enum
import urllib.parse
import aiohttp
import sanic
from npf_renderer.utils import BASIC_LAYOUT_CSS

from src import hyperblur_extractor, exceptions

# ponytail: consolidated single-file routes module -> multi-file routes directory & subdirectories

# 1. Assets Blueprint
assets = sanic.Blueprint("assets", url_prefix="/assets")
assets.static("/", "assets")

@assets.get("/css/base-post-layout.css")
async def base_post_layout(request):
    return sanic.response.text(BASIC_LAYOUT_CSS, content_type="text/css")

@assets.on_response
def add_assets_cache(request, response):
    response.headers["Cache-Control"] = "max-age=2629800, immutable"


# 2. Explore Blueprint
explore = sanic.Blueprint("explore", url_prefix="/explore")

async def _handle_explore(request, endpoint, post_type=None):
    app = request.app
    raw_endpoint = endpoint
    if continuation := request.args.get("continuation"):
        continuation = urllib.parse.unquote(continuation)

    match raw_endpoint:
        case "explore._trending":
            raw = await request.app.ctx.TumblrAPI.explore_trending(continuation=continuation)
            timeline = hyperblur_extractor.parse_timeline(raw)
            title = "Trending topics"
        case "explore._today":
            raw = await request.app.ctx.TumblrAPI.explore_today(continuation=continuation)
            timeline = hyperblur_extractor.parse_timeline(raw)
            title = "Today on Tumblr"
        case _:
            raw = await request.app.ctx.TumblrAPI.explore_post(continuation=continuation, post_type=post_type)
            timeline = hyperblur_extractor.parse_timeline(raw)
            title = "Trending topics"

    return await request.app.ctx.render(
        "timeline",
        context={"app": app, "title": title, "timeline": timeline},
    )

@explore.get("/")
async def _main_explore(request):
    return sanic.redirect(request.app.url_for("explore._trending"))

@explore.get("/trending")
async def _trending(request):
    return await _handle_explore(request, "explore._trending")

@explore.get("/today")
async def _today(request):
    return await _handle_explore(request, "explore._today")

@explore.get("/text")
async def _text(request):
    return await _handle_explore(request, "explore._text", hyperblur_extractor.ExplorePostTypeFilters.TEXT)

@explore.get("/photos")
async def _photos(request):
    return await _handle_explore(request, "explore._photos", hyperblur_extractor.ExplorePostTypeFilters.PHOTOS)

@explore.get("/gifs")
async def _gifs(request):
    return await _handle_explore(request, "explore._gifs", hyperblur_extractor.ExplorePostTypeFilters.GIFS)

@explore.get("/quotes")
async def _quotes(request):
    return await _handle_explore(request, "explore._quotes", hyperblur_extractor.ExplorePostTypeFilters.QUOTES)

@explore.get("/chats")
async def _chats(request):
    return await _handle_explore(request, "explore._chats", hyperblur_extractor.ExplorePostTypeFilters.CHATS)

@explore.get("/audio")
async def _audio(request):
    return await _handle_explore(request, "explore._audio", hyperblur_extractor.ExplorePostTypeFilters.AUDIO)

@explore.get("/video")
async def _video(request):
    return await _handle_explore(request, "explore._video", hyperblur_extractor.ExplorePostTypeFilters.VIDEO)

@explore.get("/asks")
async def _asks(request):
    return await _handle_explore(request, "explore._asks", hyperblur_extractor.ExplorePostTypeFilters.ASKS)





# 4. Miscellaneous Blueprint
miscellaneous = sanic.Blueprint("miscellaneous", url_prefix="/")

@miscellaneous.get(r"/at/<path:path>")
async def _at_links(request: sanic.Request, path: str):
    response = await request.app.ctx.TumblrAtClient.head(f"/{path}")
    if response.status == 301:
        location = urllib.parse.urlparse(response.headers["location"])
        if location.path.startswith("/"):
            return sanic.redirect(location.path)
    raise exceptions.TumblrInvalidRedirect()

@miscellaneous.get(r"/post/<post_id:int>")
async def _post_lookup(request: sanic.Request, post_id: int):
    url = f"https://www.tumblr.com/post/{post_id}"
    try:
        async with request.app.ctx.TumblrAPI.client.head(url, allow_redirects=False) as response:
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


# 5. Search Blueprint
search = sanic.Blueprint("search", url_prefix="/search")

@search.get("/")
async def query_param_redirect(request: sanic.Request):
    if query := request.args.get("q"):
        return sanic.redirect(request.app.url_for("search._main", query=urllib.parse.quote(query, safe="")))
    return sanic.redirect(request.app.url_for("explore._trending"))

@search.get("/<query:str>", name="_main")
async def _main_search(request: sanic.Request, query: str):
    query = urllib.parse.unquote(query)
    time_filter = request.args.get("t")
    if not time_filter or time_filter not in ("365", "180", "30", "7", "1"):
        time_filter = 0
    timeline = await _query_search(request, query, days=time_filter)
    return await _render_search(request, timeline, query, time_filter=time_filter, sort_by="popular", post_filter=None)

@search.get("/<query:str>/recent")
async def _sort_by_search(request: sanic.Request, query: str):
    query = urllib.parse.unquote(query)
    time_filter = request.args.get("t")
    if not time_filter or time_filter not in ("365", "180", "30", "7", "1"):
        time_filter = 0
    timeline = await _query_search(request, query, days=time_filter, latest=True)
    return await _render_search(request, timeline, query, time_filter=time_filter, sort_by="recent", post_filter=None)

@search.get("/<query:str>/<post_filter:str>")
async def _filter_by_search(request: sanic.Request, query: str, post_filter: str):
    return await _request_search_filter_post(request, query, post_filter, latest=False)

@search.get("/<query:str>/recent/<post_filter:str>")
async def _sort_by_and_filter_search(request: sanic.Request, query: str, post_filter: str):
    return await _request_search_filter_post(request, query, post_filter, latest=True)

async def _request_search_filter_post(request, query, post_filter, latest):
    query = urllib.parse.unquote(query)
    post_filter = urllib.parse.unquote(post_filter)
    time_filter = request.args.get("t")
    PostFiltersEnum = hyperblur_extractor.PostTypeFilters
    post_filter = post_filter.upper()

    if post_filter == "ASK":
        post_filter = PostFiltersEnum.ANSWER
    else:
        post_filter = getattr(PostFiltersEnum, post_filter, None)

    if not post_filter:
        if latest:
            url = request.app.url_for("search._sort_by_search", query=urllib.parse.quote(query))
        else:
            url = request.app.url_for("search._main", query=urllib.parse.quote(query))
        url += f"?{request.query_string}" if request.query_string else ""
        return sanic.redirect(url)

    if not time_filter or time_filter not in ("365", "180", "30", "7", "1"):
        time_filter = 0

    timeline = await _query_search(request, query, days=time_filter, post_type_filter=post_filter, latest=latest)
    post_filter = "ask" if post_filter == PostFiltersEnum.ANSWER else post_filter.name.lower()
    sort_by = "recent" if latest else "popular"
    return await _render_search(request, timeline, query, post_filter=post_filter, time_filter=time_filter, sort_by=sort_by)

async def _query_search(request, query, **kwargs):
    if continuation := request.args.get("continuation"):
        continuation = urllib.parse.unquote(continuation)
    raw = await request.app.ctx.TumblrAPI.timeline_search(
        query, hyperblur_extractor.TimelineType.POST, continuation=continuation, **kwargs
    )
    return hyperblur_extractor.parse_timeline(raw)

async def _render_search(request, timeline, query, **kwargs):
    if request.args.get("continuation"):
        del request.args["continuation"]
    context = {"app": request.app, "timeline": timeline, "query_args": request.args, "query": query}
    context.update(kwargs)
    return await request.app.ctx.render("search", context=context)


# 6. Tagged Blueprint
tagged = sanic.Blueprint("tagged", url_prefix="/tagged")

@tagged.get("/<tag:str>")
async def _main_tagged(request: sanic.Request, tag: str):
    tag = urllib.parse.unquote(tag)
    sort_by = request.args.get("sort")
    if continuation := request.args.get("continuation"):
        continuation = urllib.parse.unquote(continuation)

    latest = (sort_by == "recent")
    sort_by = "recent" if latest else "top"

    raw = await request.app.ctx.TumblrAPI.hubs_timeline(tag, latest=latest, continuation=continuation)
    timeline = hyperblur_extractor.parse_timeline(raw)
    if request.args.get("continuation"):
        del request.args["continuation"]

    return await request.app.ctx.render(
        "tagged",
        context={"app": request.app, "query_args": request.args, "timeline": timeline, "tag": tag, "sort_by": sort_by},
    )


# 7. Blogs & Blog Post Blueprints
blogs = sanic.Blueprint("blogs", url_prefix="")

@blogs.get("/")
async def _blog_posts(request: sanic.Request, blog: str):
    blog = urllib.parse.unquote(blog)
    continuation = urllib.parse.unquote(request.args["continuation"]) if request.args.get("continuation") else None
    before_id = urllib.parse.unquote(request.args["before_id"]) if request.args.get("before_id") else None

    raw = await request.app.ctx.TumblrAPI.blog_posts(blog, continuation=continuation, before_id=before_id)
    blog_timeline = hyperblur_extractor.parse_blog_timeline(raw)
    return await request.app.ctx.render("blog/blog", context={"app": request.app, "blog": blog_timeline})

@blogs.get("/tagged/<tag:str>")
async def _blog_tags(request: sanic.Request, blog: str, tag: str):
    blog = urllib.parse.unquote(blog)
    tag = urllib.parse.unquote(tag)
    continuation = urllib.parse.unquote(request.args["continuation"]) if request.args.get("continuation") else None

    raw = await request.app.ctx.TumblrAPI.blog_posts(blog, continuation=continuation, tag=tag)
    blog_timeline = hyperblur_extractor.parse_blog_timeline(raw)
    return await request.app.ctx.render("blog/blog", context={"app": request.app, "blog": blog_timeline, "tag": tag})

@blogs.get("/search/<query:str>")
async def _blog_search(request: sanic.Request, blog: str, query: str):
    blog = urllib.parse.unquote(blog)
    query = urllib.parse.unquote(query)
    continuation = urllib.parse.unquote(request.args["continuation"]) if request.args.get("continuation") else None

    try:
        raw = await request.app.ctx.TumblrAPI.blog_search(blog, query, continuation=continuation)
        blog_timeline = hyperblur_extractor.parse_blog_timeline(raw, is_search=True)
    except IndexError:
        raw_blog = await request.app.ctx.TumblrAPI.blog_posts(blog)
        blog_info = hyperblur_extractor.parse_blog_timeline(raw_blog).blog_info
        blog_timeline = hyperblur_extractor.BlogTimeline(blog_info=blog_info, posts=[], total_posts=0)

    return await request.app.ctx.render(
        "blog/blog_search", context={"app": request.app, "blog": blog_timeline, "blog_search_query": query}
    )

@blogs.get("/search")
async def blog_search_query_param_redirect(request: sanic.Request, blog: str):
    if query := request.args.get("q"):
        return sanic.redirect(request.app.url_for("blogs._blog_search", blog=blog, query=urllib.parse.quote(query, safe="")))
    return sanic.redirect(f"/{blog}")


# Blog Post Blueprint
blog_post_bp = sanic.Blueprint("blog_post", url_prefix="/<post_id:int>")

class PostNoteTypes(enum.Enum):
    REPLIES = 0
    REBLOGS = 1
    LIKES = 2

def get_blog_post_path(request):
    post_path = f"/{'/'.join(str(v) for v in request.match_info.values())}"
    if request.query_string:
        post_path += f"?{request.query_string}"
    return post_path

@blog_post_bp.on_request
async def handle_post_slug(request):
    blog = urllib.parse.unquote(request.match_info["blog"])
    post_id = request.match_info["post_id"]
    try:
        raw = await request.app.ctx.TumblrAPI.blog_post(blog, post_id)
        post = hyperblur_extractor.parse_timeline(raw).elements[0]
    except Exception:
        avatar_list = [{"url": "/assets/images/anon_96px.png"}] * 10
        blog_obj = hyperblur_extractor.Blog(name=blog, title=blog, avatar=avatar_list)
        post = hyperblur_extractor.Post(
            id=int(post_id),
            blog=blog_obj,
            slug="",
            date="",
            timestamp=0,
            post_url=f"{blog}/{post_id}",
            short_url=f"https://tmblr.co/{post_id}",
            reblog_key="",
            tags=(),
            content=(),
            layout=(),
            community_label_categories=(),
            note_count=0,
        )

    if slug := request.match_info.get("slug"):
        slug = urllib.parse.unquote(slug)
        if slug != post.slug:
            if not post.slug:
                del request.match_info["slug"]
                return sanic.redirect(get_blog_post_path(request))
            else:
                request.match_info["slug"] = post.slug
                return sanic.redirect(get_blog_post_path(request))
    elif post.slug:
        request.match_info["slug"] = post.slug
        return sanic.redirect(get_blog_post_path(request))

    request.ctx.post_path = request.path
    request.ctx.parsed_post = post

@blog_post_bp.on_request
async def handle_post_args(request):
    request.ctx.breq_jinja_context = jinja_context = {"post_url": request.ctx.post_path[1:]}
    args = request.args
    fetch_polls = args.get("fetch_polls")
    jinja_context["request_poll_data"] = bool(fetch_polls and sanic.utils.str_to_bool(fetch_polls))


    if note_type := args.get("note_viewer"):
        note_type = getattr(PostNoteTypes, note_type.upper(), None)
        match note_type:
            case PostNoteTypes.REPLIES:
                return await _blog_post_replies(request, **request.match_info)
            case PostNoteTypes.REBLOGS:
                return await blog_post_reblog_notes(request, **request.match_info)
            case PostNoteTypes.LIKES:
                return await blog_post_like_notes(request, **request.match_info)

@blog_post_bp.get("/")
@blog_post_bp.get("/<slug:str>", name="_blog_post_with_slug")
async def _blog_post(request: sanic.Request, **kwargs):
    blog_info = hyperblur_extractor.BlogTimeline(request.ctx.parsed_post.blog, (), None, None)
    if note_type := request.args.get("note_viewer"):
        note_type = getattr(PostNoteTypes, note_type.upper(), None)
        match note_type:
            case PostNoteTypes.REPLIES:
                return await _blog_post_replies(request, **kwargs)
            case PostNoteTypes.REBLOGS:
                return await blog_post_reblog_notes(request, **kwargs)
            case PostNoteTypes.LIKES:
                return await blog_post_like_notes(request, **kwargs)

    return await request.app.ctx.render(
        "blog/blog_post", context={"app": request.app, "blog": blog_info, "element": request.ctx.parsed_post}
    )

async def _blog_post_replies(request: sanic.Request, blog: str, post_id: str, **kwargs):
    blog = urllib.parse.unquote(blog)
    args = request.get_args(keep_blank_values=True)
    latest = ("latest" in args)
    after_id = args.get("after")
    raw = await request.app.ctx.TumblrAPI.blog_post_replies(blog, post_id, after_id=after_id, latest=latest)
    parsed_notes = hyperblur_extractor.parse_note_timeline(raw)
    return await request.app.ctx.render(
        "post/notes/viewer/viewer_page",
        context={"app": request.app, "blog_info": request.ctx.parsed_post.blog, "post_id": str(post_id), "latest": latest, "note_type": "replies", "notes": parsed_notes},
    )

async def blog_post_reblog_notes(request: sanic.Request, blog: str, post_id: str, **kwargs):
    blog = urllib.parse.unquote(blog)
    args_to_tumblr_api_wrapper = {}
    args = request.get_args(keep_blank_values=True)
    reblog_note_types = hyperblur_extractor.ReblogNoteTypes

    match reblog_filter := args.get("reblog_filter"):
        case "reblogs_with_comments":
            mode = reblog_note_types.REBLOGS_WITH_COMMENTS
        case "reblogs_with_content_comments":
            mode = reblog_note_types.REBLOGS_WITH_CONTENT_COMMENTS
        case "reblogs_only":
            mode = reblog_note_types.REBLOGS_ONLY
        case _:
            reblog_filter = None
            mode = None

    if mode == reblog_note_types.REBLOGS_ONLY:
        args_to_tumblr_api_wrapper["return_likes"] = False
    elif mode:
        args_to_tumblr_api_wrapper["mode"] = mode

    if before_timestamp := args.get("before_timestamp"):
        args_to_tumblr_api_wrapper["before_timestamp"] = before_timestamp

    if mode == reblog_note_types.REBLOGS_ONLY:
        raw = await request.app.ctx.TumblrAPI.blog_notes(blog, post_id, **args_to_tumblr_api_wrapper)
    else:
        raw = await request.app.ctx.TumblrAPI.blog_post_notes_timeline(blog, post_id, **args_to_tumblr_api_wrapper)
    parsed_notes = hyperblur_extractor.parse_note_timeline(raw)

    return await request.app.ctx.render(
        "post/notes/viewer/viewer_page",
        context={"app": request.app, "blog_info": request.ctx.parsed_post.blog, "post_id": str(post_id), "note_type": "reblogs", "reblog_filter": reblog_filter, "notes": parsed_notes},
    )

async def blog_post_like_notes(request: sanic.Request, blog: str, post_id: str, **kwargs):
    blog = urllib.parse.unquote(blog)
    raw = await request.app.ctx.TumblrAPI.blog_notes(blog, post_id, before_timestamp=request.args.get("before_timestamp"))
    parsed_notes = hyperblur_extractor.parse_note_timeline(raw)
    return await request.app.ctx.render(
        "post/notes/viewer/viewer_page",
        context={"app": request.app, "blog_info": request.ctx.parsed_post.blog, "post_id": str(post_id), "note_type": "likes", "notes": parsed_notes},
    )

blogs_group = sanic.Blueprint.group(
    blogs, blog_post_bp, url_prefix=r"/<blog:([a-z\d]{1}[a-z\d-]{0,30}[a-z\d]{0,1})>"
)


# 8. API Misc Blueprint
api_misc = sanic.Blueprint("api_misc", url_prefix="/")

@api_misc.get(r"/poll/<blog:([a-z\d]{1}[a-z\d-]{0,30}[a-z\d]{0,1})>/<post_id:int>/<poll_id:str>/results")
async def poll_results(request, blog: str, post_id: int, poll_id: int):
    blog = urllib.parse.unquote(blog)
    poll_id = urllib.parse.unquote(poll_id)
    raw = await request.app.ctx.TumblrAPI.poll_results(blog, post_id, poll_id)
    return sanic.response.json(raw["response"], headers={"Cache-Control": "max-age=600, immutable"})


BLUEPRINTS = [assets, explore, search, tagged, miscellaneous, blogs_group, api_misc]
