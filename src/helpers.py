import copy
import datetime
import urllib.parse
from typing import Optional, Dict, Any, Sequence

import dominate.tags
import dominate.util
import npf_renderer
import sanic
import sanic_ext


def is_tumblr_url(url: str | urllib.parse.ParseResult):
    """Checks URL is a tumblr URL"""
    if isinstance(url, str):
        if "tumblr.com" not in url:
            return False
        url = urllib.parse.urlparse(url)
    elif not isinstance(url, urllib.parse.ParseResult):
        return False

    hostname = url.hostname
    if hostname and (hostname == "tumblr.com" or hostname.endswith(".tumblr.com")):
        return True
    return False


def url_handler(url: str | urllib.parse.ParseResult):
    """Change URLs found in posts to privacy-friendly alternatives"""
    if isinstance(url, str):
        if url.startswith("/"):
            return url
        if "href.li" in url or "t.umblr.com" in url:
            url_obj = urllib.parse.urlparse(url)
            hostname = url_obj.hostname or ""
            try:
                if hostname.endswith("href.li"):
                    return url_handler(url_obj.query)
                elif hostname.endswith("t.umblr.com"):
                    parsed_query = urllib.parse.parse_qs(url_obj.query)
                    if redirect_url := parsed_query.get("z"):
                        return url_handler(redirect_url[0])
            except AttributeError:
                pass
            url = url_obj
        elif "tumblr.com" in url:
            scheme_end = url.find("://")
            if scheme_end != -1:
                after_scheme = url[scheme_end + 3:]
                slash_pos = after_scheme.find("/")
                if slash_pos != -1:
                    hostname = after_scheme[:slash_pos]
                    path = after_scheme[slash_pos:]
                else:
                    hostname = after_scheme
                    path = ""

                if hostname.endswith(".media.tumblr.com"):
                    sub_domains = hostname.split(".")
                    if sub_domains[1] == "media":
                        return f"/tblr/media/{sub_domains[0]}{path}"
                    elif sub_domains[0] == "www" and sub_domains[2] == "media":
                        return f"/tblr/media/{sub_domains[1]}{path}"
                elif hostname.endswith("assets.tumblr.com"):
                    return f"/tblr/assets{path}"
                elif hostname.endswith("static.tumblr.com"):
                    return f"/tblr/static{path}"
                elif hostname.startswith("a."):
                    return f"/tblr/a{path}"
                elif hostname.endswith("tumblr.com"):
                    sub_domains = hostname.split(".")
                    potential_blog_name = sub_domains[1] if sub_domains[0] == "www" else sub_domains[0]
                    if potential_blog_name != "tumblr":
                        if path.startswith("/post"):
                            return f"/{potential_blog_name}{path[5:]}"
                        else:
                            return f"/{potential_blog_name}{path}"
                    else:
                        return path
            url = urllib.parse.urlparse(url)
        else:
            return url
    elif not isinstance(url, urllib.parse.ParseResult):
        raise ValueError

    hostname = url.hostname or ""

    try:
        if hostname.endswith("href.li"):
            return url_handler(url.query)
        elif hostname.endswith("t.umblr.com"):
            parsed_query = urllib.parse.parse_qs(url.query)
            if redirect_url := parsed_query.get("z"):
                return url_handler(redirect_url[0])
    except AttributeError:
        pass

    if hostname.endswith("tumblr.com"):
        if hostname.endswith(".media.tumblr.com"):
            sub_domains = hostname.split(".")
            if sub_domains[1] == "media":
                return f"/tblr/media/{sub_domains[0]}{url.path}"
            elif sub_domains[0] == "www" and sub_domains[2] == "media":
                return f"/tblr/media/{sub_domains[1]}{url.path}"

        if hostname.endswith("assets.tumblr.com"):
            return f"/tblr/assets{url.path}"
        elif hostname.endswith("static.tumblr.com"):
            return f"/tblr/static{url.path}"
        elif hostname.startswith("a."):
            return f"/tblr/a{url.path}"
        else:
            sub_domains = hostname.split(".")
            potential_blog_name = sub_domains[1] if sub_domains[0] == "www" else sub_domains[0]

            if potential_blog_name != "tumblr":
                if url.path.startswith("/post"):
                    return f"/{potential_blog_name}{url.path[5:]}"
                else:
                    return f"/{potential_blog_name}{url.path}"
            else:
                return f"{url.path}"

    return url.geturl()


def create_reblog_attribution_link(post):
    """Creates an attribution of who the author reblogged the post from"""
    reblog_from_url = urllib.parse.urlparse(post.reblog_from.post_url)
    reblog_attribution_element_classes = ["link", "blog-name"]

    if post.reblog_from.blog_name:
        reblogged_from_name = post.reblog_from.blog_name
    else:
        reblogged_from_name = "reblogged"
        reblog_attribution_element_classes.append("hidden-reblog")

    if not is_tumblr_url(reblog_from_url):
        if (post.reblog_root.post_id == post.reblog_from.post_id) and post.reblog_root.blog_name:
            reblog_from_url = f"/{post.reblog_root.blog_name}/{post.reblog_from.id}"
        else:
            return dominate.tags.span(reblogged_from_name, cls="blog-name hidden-reblog")

    return dominate.tags.a(
        reblogged_from_name,
        href=url_handler(reblog_from_url),
        cls=" ".join(reblog_attribution_element_classes),
    )


def update_query_params(base_query_args, key, value=None):
    if isinstance(base_query_args, str):
        base_query_args = urllib.parse.parse_qs(base_query_args)
    else:
        try:
            base_query_args = dict(base_query_args)
        except Exception:
            base_query_args = base_query_args.copy() if hasattr(base_query_args, "copy") else copy.copy(base_query_args)

    if isinstance(key, dict):
        for k, v in key.items():
            if isinstance(v, (list, tuple)):
                base_query_args[k] = v
            else:
                base_query_args[k] = [v]
    else:
        if isinstance(value, (list, tuple)):
            base_query_args[key] = value
        else:
            base_query_args[key] = [value]

    return urllib.parse.urlencode(base_query_args, doseq=True)


def remove_query_params(base_query_args, key):
    base_query_args = base_query_args.copy() if hasattr(base_query_args, "copy") else copy.copy(base_query_args)
    if base_query_args.get(key):
        del base_query_args[key]
    return urllib.parse.urlencode(base_query_args, doseq=True)


def deseq_urlencode(query_args):
    return urllib.parse.urlencode(query_args, doseq=True)


def prefix_slash_in_url_if_missing(url):
    if not url.startswith("/"):
        return f"/{url}"
    return url


async def create_poll_callback(ctx, blog, post_id):
    async def poll_callable(poll_id, expiration_timestamp):
        initial_results = await ctx.TumblrAPI.poll_results(blog, post_id, poll_id)
        return initial_results["response"]
    return poll_callable



async def render_template(template: str = "", context: Optional[Dict[str, Any]] = None, **kwargs):
    jinja_context = context or {}
    request = sanic.Request.get_current()
    jinja_context.update(getattr(request.ctx, "breq_jinja_context", {}))

    if (request.route and hasattr(request.route.ctx, "rss")) or hasattr(request.ctx, "rss"):
        template = getattr(request.route.ctx, "template", None) or template
        template = f"rss/{template}.xml"
        kwargs["content_type"] = "application/rss+xml"

        if not (page_url := getattr(request.ctx, "page_url", None)):
            base_path = request.app.url_for(request.endpoint[:-4], **request.match_info)
            page_url = f"{request.app.ctx.HYPERBLUR_CONFIG.deployment.domain or ''}{base_path}"
            if request.query_string:
                page_url += f"?{request.query_string}"

        jinja_context["page_url"] = page_url

        if (elements := jinja_context.get("blog")) and elements.posts:
            jinja_context["updated"] = elements.posts[-1].date
        elif (elements := jinja_context.get("timeline")) and elements.elements:
            jinja_context["updated"] = elements.elements[-1].date
        elif (elements := jinja_context.get("notes")) and elements.notes:
            jinja_context["updated"] = elements.notes[-1].date
        else:
            jinja_context["updated"] = datetime.datetime.now(tz=datetime.timezone.utc)

    template = f"{template}.jinja"
    return await sanic_ext.render(template, context=jinja_context, app=request.app, **kwargs)



class NPFParser(npf_renderer.parse.Parser):
    def __init__(self, content, poll_callback=None):
        super().__init__(content, poll_callback)

    async def _parse_poll_block(self):
        poll_id = self.current.get("clientId") or self.current.get("client_id")
        if poll_id is None:
            raise ValueError("Invalid poll ID")

        question = self.current["question"]
        answers = {}
        for raw_ans in self.current["answers"]:
            answer_id = raw_ans.get("clientId") or raw_ans.get("client_id")
            answer_text = raw_ans.get("answerText") or raw_ans.get("answer_text")
            if answer_id is None or answer_text is None:
                raise ValueError("Invalid poll answer")
            answers[answer_id] = answer_text

        creation_timestamp = self.current["timestamp"]
        expires_after = self.current["settings"]["expireAfter"]
        votes = None
        total_votes = None

        if self.poll_result_callback:
            callback_response = await self.poll_result_callback(
                poll_id, creation_timestamp + expires_after
            )
            raw_results = callback_response["results"].items()
            processed_results = sorted(raw_results, key=lambda item: -item[1])
            votes_dict = {}
            total_votes = 0

            for index, results in enumerate(processed_results):
                vote_count = results[1]
                total_votes += vote_count
                votes_dict[results[0]] = npf_renderer.objects.poll_block.PollResult(
                    is_winner=(index == 0), vote_count=vote_count
                )

            votes = npf_renderer.objects.poll_block.PollResults(
                timestamp=callback_response["timestamp"], results=votes_dict
            )

        return npf_renderer.objects.poll_block.PollBlock(
            poll_id=poll_id,
            question=question,
            answers=answers,
            creation_timestamp=int(creation_timestamp),
            expires_after=int(expires_after),
            votes=votes,
            total_votes=total_votes,
        )

    async def __parse_block(self):
        match self.current["type"]:
            case "text":
                block = self._parse_text()
            case "image":
                block = self._parse_image_block()
            case "link":
                block = self._parse_link_block()
            case "audio":
                block = self._parse_audio_block()
            case "video":
                block = self._parse_video_block()
            case "poll":
                block = await self._parse_poll_block()
            case _:
                block = npf_renderer.objects.unsupported.Unsupported(self.current["type"])

        self.parsed_result.append(block)

    async def parse(self):
        while self.next():
            await self.__parse_block()
        return self.parsed_result


class NPFFormatter(npf_renderer.format.Formatter):
    def __init__(
        self,
        content,
        layout=None,
        *,
        blog_name=None,
        post_id=None,
        url_handler=None,
        forbid_external_iframes=False,
        request=None,
    ):
        initialization_arguments = {
            "content": content,
            "layout": layout,
            "url_handler": url_handler,
            "forbid_external_iframes": forbid_external_iframes,
        }
        if request:
            initialization_arguments["truncate"] = False

        super().__init__(**initialization_arguments)
        self.blog_name = blog_name
        self.post_id = post_id

    def _format_poll(self, block):
        poll_html = super()._format_poll(block)
        poll_html["data-poll-id"] = block.poll_id

        poll_choices = poll_html[1][0]
        for index, answer_id in enumerate(block.answers.keys()):
            poll_choices[index]["data-answer-id"] = answer_id

        if (self.blog_name and self.post_id) and not block.votes:
            poll_footer = poll_html[2]
            no_script_fallback = dominate.tags.noscript(
                dominate.tags.a(
                    "See Results",
                    href=f"/{self.blog_name}/{self.post_id}?fetch_polls=true",
                    cls="toggle-poll-results",
                )
            )
            poll_footer.children.insert(0, no_script_fallback)

        return poll_html

    def _format_image(self, block, row_length=1, override_aspect_ratio=None):
        image_html = super()._format_image(block, row_length, override_aspect_ratio)
        try:
            image_element = image_html.getElementsByTagName("img")
            image_container = image_html.get(cls="image-container")
            if not (image_container and image_element):
                return image_html

            image_container = image_container[0]
            image_element = image_element[0]
            image_element["loading"] = "eager"
            image_element["decoding"] = "sync"

            self._add_alt_text_element(block, image_container)
            self._linkify_images(image_container, image_element)
        except (ValueError, IndexError):
            pass

        return image_html

    def _linkify_images(self, image_container, image_element):
        index_of_image = image_container.children.index(image_element)
        image_container[index_of_image] = dominate.tags.a(image_element, href=image_element.src)

    def _add_alt_text_element(self, block, image_container):
        if block.alt_text and block.alt_text != "image":
            image_container.add(
                dominate.tags.div(
                    dominate.tags.details(
                        dominate.tags.summary("ALT", title=f"{block.alt_text}"),
                        dominate.tags.p(block.alt_text),
                    ),
                    cls="img-alt-text",
                )
            )

    def _format_video(self, block):
        video_block = super()._format_video(block)
        if block.media:
            try:
                media_url = block.media[0].url
                proxied_url = self.url_handler(media_url)
                download_btn = dominate.tags.a(
                    dominate.util.raw('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path><polyline points="7 10 12 15 17 10"></polyline><line x1="12" y1="15" x2="12" y2="3"></line></svg>'),
                    href=proxied_url,
                    download="",
                    cls="video-download-btn",
                    title="Download Video"
                )
                video_block.add(download_btn)
            except Exception:
                pass
        return video_block


async def format_npf(
    contents, layouts=None, blog_name=None, post_id=None, *, poll_callback=None, request=None
):
    try:
        contents = await NPFParser(contents, poll_callback=poll_callback).parse()
        if layouts:
            layouts = npf_renderer.parse.LayoutParser(layouts).parse()

        render_error = None
        formatted = NPFFormatter(
            contents,
            layouts,
            blog_name=blog_name,
            post_id=post_id,
            url_handler=url_handler,
            forbid_external_iframes=True,
            request=request,
        ).format()
    except Exception as e:
        formatted = dominate.tags.div(cls="post-body has-error")
        render_error = request.app.ctx.create_user_friendly_error_message(request, e)

    return render_error, formatted.render(pretty=False)
