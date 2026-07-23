import datetime
import enum
import json
import logging
import time
import urllib.parse
from typing import Optional, Union, NamedTuple, Sequence, List, Tuple

import aiohttp

# ponytail: consolidated single-file extractor module -> multi-file hyperblur_extractor directory

logger = logging.getLogger("hyperblur-extractor")
logger.setLevel(logging.WARNING)

# Helper function
def dig_dict(target, keys: List | Tuple):
    for key in keys:
        if isinstance(target, dict):
            target = target.get(key)
        else:
            return None
    return target


# Exceptions
class InitialTumblrAPIParseException(Exception):
    def __init__(self, message):
        super().__init__(message)


class TumblrErrorResponse(Exception):
    def __init__(self, message, code, details, internal_code):
        message = f"Tumblr has returned an error response\nHTTP Code: {code}\nMessage: {message}"
        self.message = message
        self.code = code
        self.details = details
        self.internal_code = internal_code
        if details:
            message += f"\nDetails: {details}"
        if internal_code:
            message += f"\nError Code: {internal_code}"
        super().__init__(message)


class TumblrBlogNotFoundError(TumblrErrorResponse):
    pass


class TumblrRestrictedTagError(TumblrErrorResponse):
    pass


class TumblrLoginRequiredError(TumblrErrorResponse):
    pass


class TumblrPasswordRequiredBlogError(TumblrErrorResponse):
    pass


class TumblrNon200NorJSONResponse(Exception):
    def __init__(self, status_code):
        self.status_code = status_code


class TumblrRatelimitReachedError(Exception):
    def __init__(self, status_code, ratelimit_reset_timestamp=None):
        self.status_code = status_code
        self.ratelimit_reset_timestamp = ratelimit_reset_timestamp


class ExtractorExceptionsModule:
    InitialTumblrAPIParseException = InitialTumblrAPIParseException
    TumblrErrorResponse = TumblrErrorResponse
    TumblrBlogNotFoundError = TumblrBlogNotFoundError
    TumblrRestrictedTagError = TumblrRestrictedTagError
    TumblrLoginRequiredError = TumblrLoginRequiredError
    TumblrPasswordRequiredBlogError = TumblrPasswordRequiredBlogError
    TumblrNon200NorJSONResponse = TumblrNon200NorJSONResponse
    TumblrRatelimitReachedError = TumblrRatelimitReachedError

exceptions = ExtractorExceptionsModule()
hyperblur_exceptions = exceptions


# Request Configuration Enums & Fields
class ExplorePostTypeFilters(enum.Enum):
    TEXT = (0,)
    PHOTOS = (1,)
    GIFS = (2,)
    QUOTES = (3,)
    CHATS = (4,)
    AUDIO = (5,)
    VIDEO = (6,)
    ASKS = 7


class PostTypeFilters(enum.Enum):
    TEXT = (0,)
    PHOTO = (1,)
    GIF = (2,)
    QUOTE = (3,)
    LINK = (4,)
    CHAT = (5,)
    AUDIO = (6,)
    VIDEO = (7,)
    ANSWER = (8,)
    POLL = 9


class TimelineType(enum.Enum):
    TAG = 0
    BLOG = 1
    POST = 2


class ReblogNoteTypes(enum.Enum):
    REBLOGS_WITH_COMMENTS = 0
    REBLOGS_WITH_CONTENT_COMMENTS = 1
    REBLOGS_ONLY = 2


EXPLORE_BLOG_INFO_FIELDS = "?advertiser_name,?avatar,?blog_view_url,?can_be_booped,?can_be_followed,?can_show_badges,?description_npf,?followed,?is_adult,?is_member,name,?primary,?theme,?title,?tumblrmart_accessories,url,?uuid,?ask,?can_submit,?can_subscribe,?is_blocked_from_primary,?is_blogless_advertiser,?is_password_protected,?share_following,?share_likes,?subscribed"
TUMBLR_SEARCH_BLOG_INFO_FIELDS = "?advertiser_name,?avatar,?blog_view_url,?can_be_booped,?can_be_followed,?can_show_badges,?description_npf,?followed,?is_adult,?is_member,name,?primary,?theme,?title,?tumblrmart_accessories,url,?uuid,?share_following,?share_likes,?ask"
POST_BLOG_INFO_FIELDS = "?advertiser_name,?avatar,?blog_view_url,?can_be_booped,?can_be_followed,?can_show_badges,?description_npf,?followed,?is_adult,?is_member,name,?primary,?theme,?title,?tumblrmart_accessories,url,?uuid,?share_likes,?share_following,?can_subscribe,?subscribed,?allow_search_indexing,?ask,?can_submit,?is_blocked_from_primary,?analytics_url,?is_hidden_from_blog_network"
BLOG_POSTS_BLOG_INFO_FIELDS = "	?advertiser_name,?avatar,?blog_view_url,?can_be_booped,?can_be_followed,?can_show_badges,?description_npf,?followed,?is_adult,?is_member,name,?primary,?theme,?title,?tumblrmart_accessories,url,?uuid,?ask,?can_submit,?can_subscribe,?is_blocked_from_primary,?is_blogless_advertiser,?is_password_protected,?share_following,?share_likes,?subscribed,?admin,?can_message,?ask_page_title,?analytics_url,?top_tags,?allow_search_indexing,?is_hidden_from_blog_network,?should_show_gift,?should_show_tumblrmart_gift"
TUMBLR_TAG_BLOG_INFO_FIELDS = EXPLORE_BLOG_INFO_FIELDS
BLOG_SEARCH_BLOG_INFO_FIELDS = EXPLORE_BLOG_INFO_FIELDS


# Data Models
VERSION = 5

class Cursor(NamedTuple):
    cursor: str
    limit: Optional[int] = None
    days: Optional[int] = None
    query: Optional[str] = None
    mode: Optional[str] = None
    timeline_type: Optional[str] = None
    skip_components: Optional[str] = None
    reblog_info: Optional[bool] = None
    post_type_filter: Optional[str] = None

    def to_json_serialisable(self):
        return self._asdict()

    @classmethod
    def from_json(cls, json):
        return cls(**json)


class HeaderInfo(NamedTuple):
    header_image: str
    focused_header_image: str
    scaled_header_image: str

    def to_json_serialisable(self):
        return self._asdict()

    @classmethod
    def from_json(cls, json):
        return cls(**json)


class BlogTheme(NamedTuple):
    avatar_shape: str
    background_color: Optional[str] = None
    body_font: Optional[str] = None
    header_info: Optional[HeaderInfo] = None

    def to_json_serialisable(self):
        json_serializable = self._asdict()
        if self.header_info:
            json_serializable["header_info"] = self.header_info.to_json_serialisable()
        return json_serializable

    @classmethod
    def from_json(cls, json):
        if json.get("header_info"):
            json["header_info"] = HeaderInfo.from_json(json["header_info"])
        return cls(**json)


class BrokenBlog(NamedTuple):
    name: str
    avatar: list[dict]

    def to_json_serialisable(self):
        return self._asdict()

    @classmethod
    def from_json(cls, json):
        return cls(**json)


class Blog(NamedTuple):
    name: str
    avatar: list[dict]
    title: str
    url: str
    is_adult: bool
    description_npf: list[dict]
    uuid: str
    theme: BlogTheme
    active: bool = False
    requires_account_to_view: Optional[bool] = False

    def to_json_serialisable(self):
        json_serializable = self._asdict()
        if json_serializable.get("theme"):
            json_serializable["theme"] = json_serializable["theme"].to_json_serialisable()
        return json_serializable

    @classmethod
    def from_json(cls, json):
        json["theme"] = BlogTheme.from_json(json["theme"])
        return cls(**json)


class Signpost(NamedTuple):
    title: str
    description: Optional[str] = None

    def to_json_serialisable(self):
        return {"title": self.title, "description": self.description}

    @classmethod
    def from_json(cls, json):
        return cls(**json)


class CommunityLabel(enum.Enum):
    MATURE = 0
    DRUG_USE = 1
    VIOLENCE = 2
    SEXUAL_THEMES = 3


class ReblogAttribution(NamedTuple):
    post_id: str
    post_url: str
    blog_name: Optional[str] = None
    blog_title: Optional[str] = None

    def to_json_serialisable(self):
        return self._asdict()

    @classmethod
    def from_json(cls, json):
        return cls(**json)


class PostTrail(NamedTuple):
    id: Optional[str]
    blog: Union[Blog, BrokenBlog]
    date: Optional[datetime.datetime]
    content: Sequence[dict]
    layout: Sequence[dict]

    def to_json_serialisable(self):
        json_serializable = self._asdict()
        json_serializable["blog"] = self.blog.to_json_serialisable()
        if self.date:
            json_serializable["date"] = self.date.replace(tzinfo=datetime.timezone.utc).timestamp()
        return json_serializable

    @classmethod
    def from_json(cls, json):
        if json.get("date") is not None:
            json["date"] = datetime.datetime.fromtimestamp(json["date"], tz=datetime.timezone.utc)

        blog_data = json["blog"]
        if "title" in blog_data:
            json["blog"] = Blog.from_json(blog_data)
        else:
            json["blog"] = BrokenBlog.from_json(blog_data)

        return cls(**json)


class Post(NamedTuple):
    blog: Blog
    id: str
    is_nsfw: bool
    is_advertisement: bool
    post_url: str
    slug: str
    date: datetime.datetime
    tags: Sequence[str]
    summary: str
    content: Sequence[dict]
    layout: Sequence[dict]
    trail: Sequence[PostTrail]
    display_avatar: bool
    reply_count: int
    reblog_count: int
    like_count: int
    note_count: int
    default_note_viewer_tab: str = "replies"
    reblog_from: Optional[ReblogAttribution] = None
    reblog_root: Optional[ReblogAttribution] = None
    community_labels: Sequence[CommunityLabel] = []

    def to_json_serialisable(self):
        json_serializable = self._asdict()
        json_serializable["blog"] = json_serializable["blog"].to_json_serialisable()
        if self.reblog_from:
            json_serializable["reblog_from"] = self.reblog_from.to_json_serialisable()
        if self.reblog_root:
            json_serializable["reblog_root"] = self.reblog_root.to_json_serialisable()

        trail = []
        for post_trail in self.trail:
            trail.append(post_trail.to_json_serialisable())
        json_serializable["trail"] = trail

        if self.date:
            json_serializable["date"] = self.date.replace(tzinfo=datetime.timezone.utc).timestamp()

        community_labels = []
        for community_label in self.community_labels:
            community_labels.append(community_label.value)
        json_serializable["community_labels"] = community_labels

        return json_serializable

    @classmethod
    def from_json(cls, json):
        json["blog"] = Blog.from_json(json["blog"])
        if json.get("reblog_from"):
            json["reblog_from"] = ReblogAttribution.from_json(json["reblog_from"])
        if json.get("reblog_root"):
            json["reblog_root"] = ReblogAttribution.from_json(json["reblog_root"])

        trail = []
        for post_trail in json["trail"]:
            trail.append(PostTrail.from_json(post_trail))
        json["trail"] = trail

        if json.get("date") is not None:
            json["date"] = datetime.datetime.fromtimestamp(json["date"], tz=datetime.timezone.utc)

        community_labels = []
        for label_value in json["community_labels"]:
            community_labels.append(CommunityLabel(label_value))
        json["community_labels"] = community_labels

        return cls(**json)


class ReplyNote(NamedTuple):
    uuid: str
    reply_id: str
    date: Optional[datetime.datetime]
    content: Optional[Sequence[dict]]
    layout: Optional[Sequence[dict]]
    blog: Blog

    def to_json_serialisable(self):
        json_serializable = self._asdict()
        json_serializable["type"] = "reply"
        json_serializable["blog"] = json_serializable["blog"].to_json_serialisable()
        if self.date:
            json_serializable["date"] = self.date.replace(tzinfo=datetime.timezone.utc).timestamp()
        return json_serializable

    @classmethod
    def from_json(cls, json):
        if json.get("date") is not None:
            json["date"] = datetime.datetime.fromtimestamp(json["date"], tz=datetime.timezone.utc)
        if json.get("blog"):
            json["blog"] = Blog.from_json(json["blog"])
        json.pop("type", None)
        return cls(**json)


class ReblogNote(NamedTuple):
    uuid: str
    id: str
    blog: Blog
    content: Optional[Sequence[dict]]
    layout: Optional[Sequence[dict]]
    tags: Sequence[str]
    reblogged_from: str
    date: Optional[datetime.datetime]
    community_labels: Sequence[CommunityLabel]

    def to_json_serialisable(self):
        json_serializable = self._asdict()
        json_serializable["type"] = "reblog"
        json_serializable["blog"] = json_serializable["blog"].to_json_serialisable()
        if self.date:
            json_serializable["date"] = self.date.replace(tzinfo=datetime.timezone.utc).timestamp()
        return json_serializable

    @classmethod
    def from_json(cls, json):
        if json.get("date") is not None:
            json["date"] = datetime.datetime.fromtimestamp(json["date"], tz=datetime.timezone.utc)
        if json.get("blog"):
            json["blog"] = Blog.from_json(json["blog"])
        community_labels = [CommunityLabel(v) for v in json.get("community_labels", [])]
        json["community_labels"] = community_labels
        json.pop("type", None)
        return cls(**json)


class LikeNote(NamedTuple):
    blog_name: str
    blog_uuid: str
    blog_title: str
    date: Optional[datetime.datetime]
    avatar: list[dict] | str

    def to_json_serialisable(self):
        json_serializable = self._asdict()
        json_serializable["type"] = "like"
        if self.date:
            json_serializable["date"] = self.date.replace(tzinfo=datetime.timezone.utc).timestamp()
        return json_serializable

    @classmethod
    def from_json(cls, json):
        if json.get("date") is not None:
            json["date"] = datetime.datetime.fromtimestamp(json["date"], tz=datetime.timezone.utc)
        json.pop("type", None)
        return cls(**json)


class BlogTimeline(NamedTuple):
    blog_info: Blog
    posts: Sequence[Post]
    total_posts: int | None
    next: Optional[Cursor] = None

    def to_json_serialisable(self):
        json_serializable = {
            "version": VERSION,
            "blog_info": self.blog_info.to_json_serialisable(),
            "posts": [post.to_json_serialisable() for post in self.posts],
            "total_posts": self.total_posts,
            "next": self.next.to_json_serialisable() if self.next else None,
        }
        return json_serializable

    @classmethod
    def from_json(cls, json):
        json["blog_info"] = Blog.from_json(json["blog_info"])
        json["posts"] = [Post.from_json(p) for p in json["posts"]]
        if json.get("next"):
            json["next"] = Cursor.from_json(json["next"])
        json.pop("version", None)
        return cls(**json)


class NoteTimeline(NamedTuple):
    notes: Sequence[ReplyNote | ReblogNote | LikeNote]
    total_notes: int
    total_replies: int
    total_reblogs: int
    total_likes: int
    before_timestamp: Optional[str] = None
    after_id: Optional[str] = None

    def to_json_serialisable(self):
        json_serializable = self._asdict()
        json_serializable["version"] = VERSION
        json_serializable["notes"] = [note.to_json_serialisable() for note in self.notes]
        return json_serializable

    @classmethod
    def from_json(cls, json):
        notes = []
        for note in json["notes"]:
            match note.get("type"):
                case "reply":
                    notes.append(ReplyNote.from_json(note))
                case "reblog":
                    notes.append(ReblogNote.from_json(note))
                case "like":
                    notes.append(LikeNote.from_json(note))
        json["notes"] = notes
        json.pop("version", None)
        return cls(**json)


class Timeline(NamedTuple):
    elements: Sequence[Post | Blog]
    signposts: Sequence[Signpost] = []
    next: Optional[Cursor] = None

    def to_json_serialisable(self):
        elements = []
        for element in self.elements:
            if isinstance(element, Post):
                elements.append({"post": element.to_json_serialisable()})
            else:
                elements.append({"blog": element.to_json_serialisable()})

        signposts = [s.to_json_serialisable() for s in self.signposts]
        next_ = self.next.to_json_serialisable() if self.next else None
        return {
            "version": VERSION,
            "elements": elements,
            "signposts": signposts,
            "next": next_,
        }

    @classmethod
    def from_json(cls, json):
        elements = []
        for element in json["elements"]:
            if post := element.get("post"):
                elements.append(Post.from_json(post))
            else:
                elements.append(Blog.from_json(element.get("blog")))
        json["elements"] = elements
        json["signposts"] = [Signpost.from_json(s) for s in json.get("signposts", [])]
        if json.get("next"):
            json["next"] = Cursor.from_json(json["next"])
        json.pop("version", None)
        return cls(**json)


# Models Module sub-namespace compatibility
class PostModule:
    Post = Post
    PostTrail = PostTrail
    ReblogAttribution = ReblogAttribution
    CommunityLabel = CommunityLabel
    ReplyNote = ReplyNote
    ReblogNote = ReblogNote
    LikeNote = LikeNote

class BlogModule:
    Blog = Blog
    BlogTheme = BlogTheme
    HeaderInfo = HeaderInfo
    BrokenBlog = BrokenBlog

class MiscModule:
    Signpost = Signpost

class TimelinesModule:
    Timeline = Timeline
    BlogTimeline = BlogTimeline
    NoteTimeline = NoteTimeline

class ExtractorModelsModule:
    post = PostModule
    blog = BlogModule
    misc = MiscModule
    timelines = TimelinesModule
    base = type("BaseModule", (), {"Cursor": Cursor, "VERSION": VERSION})

models = ExtractorModelsModule()


# Parsers
class BlogParser:
    def __init__(self, target) -> None:
        self.target = target

    @classmethod
    def process(cls, initial_data):
        if initial_data.get("objectType") == "blog":
            return cls(initial_data["resources"][0]).parse()
        return None

    def parse_theme(self):
        target = self.target.get("theme")
        avatar_shape = target["avatarShape"]
        if header_image := target.get("headerImage"):
            header_info = HeaderInfo(
                header_image,
                target["headerImageFocused"],
                target["headerImageScaled"],
            )
            return BlogTheme(
                avatar_shape=avatar_shape,
                background_color=target["backgroundColor"],
                body_font=target["bodyFont"],
                header_info=header_info,
            )
        return BlogTheme(avatar_shape=avatar_shape, background_color=None, body_font=None, header_info=None)

    def parse(self):
        return Blog(
            name=self.target["name"],
            avatar=self.target["avatar"],
            title=self.target["title"],
            url=self.target["url"],
            is_adult=self.target["isAdult"],
            description_npf=self.target["descriptionNpf"],
            uuid=self.target["uuid"],
            theme=self.parse_theme(),
            active=self.target.get("active", True),
            requires_account_to_view=self.target.get("isHiddenFromBlogNetwork"),
        )

    def parse_limited(self):
        return Blog(
            name=self.target["name"],
            avatar=self.target["avatar"],
            title=self.target.get("title", ""),
            url=self.target.get("url", ""),
            is_adult=self.target.get("isAdult", False),
            description_npf=self.target.get("descriptionNpf", ""),
            uuid=self.target.get("uuid"),
            theme=self.parse_theme(),
            active=self.target.get("active", True),
        )


class PostParser:
    def __init__(self, target) -> None:
        self.target = target

    @classmethod
    def process(cls, initial_data):
        if initial_data.get("objectType") == "post":
            return cls(initial_data).parse()
        return None

    @staticmethod
    def parse_community_label(initial_data):
        community_labels = []
        if raw_labels := initial_data.get("communityLabels"):
            if raw_labels["hasCommunityLabel"]:
                for category in raw_labels["categories"]:
                    label = getattr(CommunityLabel, category.upper(), None)
                    if label:
                        community_labels.append(label)
                if not community_labels:
                    community_labels.append(CommunityLabel.MATURE)
        return community_labels

    def parse(self):
        blog = BlogParser(self.target["blog"]).parse()
        id = self.target["id"]
        note_count = self.target.get("noteCount")
        reply_count = self.target.get("replyCount")
        reblog_count = self.target.get("reblogCount")
        like_count = self.target.get("likeCount")
        default_note_viewer_tab = "replies"

        for tab, counts in zip(("replies", "reblogs", "likes"), (reply_count, reblog_count, like_count)):
            if counts and counts > 0:
                default_note_viewer_tab = tab
                break

        is_advertisement = bool(
            self.target.get("advertiserId") or self.target.get("adId") or self.target.get("adProviderId")
        )
        content = self.target["content"]
        layout = self.target["layout"]
        trail = self.target["trail"]

        trails = []
        for trail_post in trail:
            is_broken_trail = False
            if raw_trail_blog := trail_post.get("blog"):
                trail_blog = BlogParser(raw_trail_blog).parse()
            else:
                trail_blog = BrokenBlog(
                    name=trail_post["brokenBlog"]["name"],
                    avatar=trail_post["brokenBlog"]["avatar"],
                )
                is_broken_trail = True

            trail_content = trail_post["content"]
            trail_layout = trail_post["layout"]

            if (trail_post_data := trail_post.get("post")) and not is_broken_trail:
                trail_post_id = trail_post_data["id"]
                trail_post_creation_date = datetime.datetime.fromtimestamp(
                    trail_post_data["timestamp"], tz=datetime.timezone.utc
                )
            else:
                trail_post_id = None
                trail_post_creation_date = None

            trails.append(
                PostTrail(
                    id=trail_post_id,
                    blog=trail_blog,
                    date=trail_post_creation_date,
                    content=trail_content,
                    layout=trail_layout,
                )
            )

        reblog_from_information = None
        reblog_root_information = None

        if reblogged_from_id := self.target.get("rebloggedFromId"):
            reblog_from_information = ReblogAttribution(
                post_id=reblogged_from_id,
                post_url=self.target["parentPostUrl"],
                blog_name=self.target["rebloggedFromName"],
                blog_title=self.target["rebloggedFromTitle"],
            )

            if root_reblogged_from_id := self.target.get("rebloggedRootId"):
                reblog_root_information = ReblogAttribution(
                    post_id=root_reblogged_from_id,
                    post_url=self.target["rebloggedRootUrl"],
                    blog_name=self.target["rebloggedRootName"],
                    blog_title=self.target["rebloggedRootTitle"],
                )

        community_labels = self.parse_community_label(self.target)

        return Post(
            blog=blog,
            id=id,
            is_nsfw=self.target["isNsfw"],
            is_advertisement=is_advertisement,
            post_url=self.target["postUrl"],
            slug=self.target["slug"],
            date=datetime.datetime.fromtimestamp(self.target["timestamp"], tz=datetime.timezone.utc),
            tags=self.target["tags"],
            summary=self.target["summary"],
            content=content,
            layout=layout,
            trail=trails,
            display_avatar=self.target["displayAvatar"],
            reply_count=reply_count,
            reblog_count=reblog_count,
            like_count=like_count,
            note_count=note_count,
            default_note_viewer_tab=default_note_viewer_tab,
            reblog_from=reblog_from_information,
            reblog_root=reblog_root_information,
            community_labels=community_labels,
        )


class ReplyNoteParser:
    def __init__(self, target) -> None:
        self.target = target

    @classmethod
    def process(cls, initial_data):
        if initial_data.get("type") == "reply":
            return cls(initial_data).parse()

    def parse(self):
        return ReplyNote(
            uuid=self.target["id"],
            reply_id=self.target["replyId"],
            date=datetime.datetime.fromtimestamp(self.target["timestamp"], tz=datetime.timezone.utc),
            content=self.target["content"],
            layout=self.target["layout"],
            blog=BlogParser(self.target["blog"]).parse_limited(),
        )


class ReblogNoteParser:
    def __init__(self, target) -> None:
        self.target = target

    @classmethod
    def process(cls, initial_data):
        if initial_data.get("type") == "reblog":
            if "blogName" in initial_data:
                return cls(initial_data).parse_simple()
            return cls(initial_data).parse()

    def parse(self) -> ReblogNote:
        return ReblogNote(
            uuid=self.target["id"],
            id=self.target["postId"],
            blog=BlogParser(self.target["blog"]).parse_limited(),
            content=self.target["content"],
            layout=self.target["content"],
            tags=self.target["tags"],
            reblogged_from=self.target["reblogParentBlogName"],
            date=datetime.datetime.fromtimestamp(self.target["timestamp"], tz=datetime.timezone.utc),
            community_labels=PostParser.parse_community_label(self.target),
        )

    def parse_simple(self):
        blog = Blog(
            name=self.target["blogName"],
            avatar=[{"url": avatar_url} for avatar_url in list(self.target["avatarUrl"].values())],
            title=self.target["blogTitle"],
            url="",
            is_adult=False,
            description_npf="",
            uuid=self.target["blogUuid"],
            theme=BlogTheme(self.target["avatarShape"]),
            active=True,
        )
        return ReblogNote(
            uuid=self.target["blogUuid"],
            id=self.target["postId"],
            blog=blog,
            content=[],
            layout=[],
            tags=self.target["tags"],
            reblogged_from=self.target["reblogParentBlogName"],
            date=datetime.datetime.fromtimestamp(self.target["timestamp"], tz=datetime.timezone.utc),
            community_labels=[],
        )


class LikeNoteParser:
    def __init__(self, target) -> None:
        self.target = target

    @classmethod
    def process(cls, initial_data):
        if initial_data.get("type") == "like":
            return cls(initial_data).parse()

    def parse(self):
        return LikeNote(
            blog_name=self.target["blogName"],
            blog_uuid=self.target["blogUuid"],
            blog_title=self.target["blogTitle"],
            date=datetime.datetime.fromtimestamp(self.target["timestamp"], tz=datetime.timezone.utc),
            avatar=self.target["avatarUrl"],
        )


class SignpostParser:
    def __init__(self, target) -> None:
        self.target = target

    @classmethod
    def process(cls, initial_data):
        if initial_data.get("objectType") == "signpost_cta":
            return cls(initial_data).parse()

    def parse(self):
        return Signpost(
            title=self.target["display"]["title"],
            description=dig_dict(self.target, ("resources", "description")),
        )


def parse_item(element, element_index=0, total_elements=1, use_parsers=None):
    if logger.isEnabledFor(10):
        item_number = f"({element_index + 1}/{total_elements})"
        logger.debug(f"parse_item: Parsing item {item_number}")
    else:
        item_number = None

    if not use_parsers:
        return PostParser.process(element)

    for parser_index, parser in enumerate(use_parsers):
        if logger.isEnabledFor(10):
            logger.debug(
                f"parse_item: Attempting to match item {item_number} with `{parser.__name__}`"
                f"({parser_index + 1}/{len(use_parsers)})..."
            )
        if parsed_element := parser.process(element):
            return parsed_element
    return None


class _CursorParser:
    def __init__(self, raw_cursor) -> None:
        self.target = raw_cursor

    @classmethod
    def process(cls, initial_data):
        if target := dig_dict(initial_data, ("links", "next")):
            return cls(target["queryParams"]).parse()
        return None

    def parse(self):
        return Cursor(
            cursor=self.target.get("cursor") or self.target.get("pageNumber"),
            limit=self.target.get("days"),
            days=self.target.get("query"),
            query=self.target.get("mode"),
            mode=self.target.get("timelineType"),
            skip_components=self.target.get("skipComponent"),
            reblog_info=self.target.get("reblogInfo"),
            post_type_filter=self.target.get("postTypeFilter"),
        )


class TimelineParser:
    def __init__(self, target) -> None:
        self.target = target

    @classmethod
    def process(cls, initial_data):
        if target := initial_data.get("timeline"):
            return cls(target).parse()
        return None

    def parse(self):
        cursor = _CursorParser.process(self.target)
        elements = []
        signposts = []
        total_raw_elements = len(self.target["elements"])
        for element_index, element in enumerate(self.target["elements"]):
            if result := parse_item(
                element,
                element_index,
                total_raw_elements,
                use_parsers=(PostParser, SignpostParser),
            ):
                if isinstance(result, Signpost):
                    signposts.append(result)
                else:
                    elements.append(result)

        return Timeline(elements=elements, signposts=signposts, next=cursor)


class BlogTimelineParser:
    def __init__(self, target) -> None:
        self.target = target

    @classmethod
    def process(cls, initial_data):
        if "blog" in initial_data:
            return cls(initial_data).parse()
        return None

    def parse(self):
        cursor = _CursorParser.process(self.target)
        blog = BlogParser(self.target["blog"]).parse()
        posts = []
        total_raw_posts = len(self.target["posts"])
        for post_index, post in enumerate(self.target["posts"]):
            if result := parse_item(post, post_index, total_raw_posts):
                posts.append(result)

        return BlogTimeline(blog_info=blog, posts=posts, total_posts=self.target.get("totalPosts"), next=cursor)

    def parse_blog_search_timeline(self):
        cursor = _CursorParser.process(self.target)
        posts = []
        total_raw_posts = len(self.target["posts"])
        for post_index, post in enumerate(self.target["posts"]):
            if result := parse_item(post, post_index, total_raw_posts):
                posts.append(result)

        return BlogTimeline(
            blog_info=posts[0].blog,
            posts=posts,
            total_posts=total_raw_posts,
            next=cursor,
        )


class NoteTimelineParser:
    def __init__(self, target) -> None:
        self.target = target

    @classmethod
    def process(cls, initial_data):
        if "timeline" in initial_data:
            return cls(initial_data).parse()
        elif "notes" in initial_data:
            return cls(initial_data).parse_note_sequence()
        return None

    def parse(self):
        timeline = self.target["timeline"]
        total_raw_notes = len(timeline["elements"])
        notes = []
        for index, note in enumerate(timeline["elements"]):
            if result := parse_item(
                note, index, total_raw_notes, use_parsers=(ReplyNoteParser, ReblogNoteParser)
            ):
                notes.append(result)

        query_for_next_batch = dig_dict(timeline, ("links", "next", "queryParams"))
        if query_for_next_batch:
            before_timestamp = query_for_next_batch.get("beforeTimestamp")
            after_id = query_for_next_batch.get("after")
        else:
            before_timestamp = None
            after_id = None

        return self.return_note_model(notes, before_timestamp=before_timestamp, after_id=after_id)

    def parse_note_sequence(self):
        sequence = self.target["notes"]
        total_raw_notes = len(sequence)
        notes = []
        for index, note in enumerate(sequence):
            if result := parse_item(
                note, index, total_raw_notes, use_parsers=(LikeNoteParser, ReblogNoteParser)
            ):
                notes.append(result)

        before_timestamp = dig_dict(self.target, ("links", "next", "queryParams", "beforeTimestamp"))
        return self.return_note_model(notes, before_timestamp=before_timestamp)

    def return_note_model(self, notes, before_timestamp=None, after_id=None):
        return NoteTimeline(
            notes=notes,
            total_notes=self.target["totalNotes"],
            total_likes=self.target["totalLikes"],
            total_reblogs=self.target["totalReblogs"],
            total_replies=self.target["totalReplies"],
            before_timestamp=before_timestamp,
            after_id=after_id,
        )


def parse_timeline(initial_data):
    return TimelineParser.process(initial_data["response"])


def parse_blog_timeline(initial_data, is_search=False):
    if is_search:
        return BlogTimelineParser(initial_data["response"]).parse_blog_search_timeline()
    return BlogTimelineParser.process(initial_data["response"])


def parse_note_timeline(initial_data):
    return NoteTimelineParser.process(initial_data["response"])


# TumblrAPI Class
class TumblrAPI:
    DEFAULT_HEADERS = {
        "accept": "application/json;format=camelcase",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:136.0) Gecko/20100101 Firefox/136.0",
        "accept-encoding": "gzip, deflate",
        "te": "trailers",
        "connection": "keep-alive",
        "referer": "https://www.tumblr.com/",
        "authorization": "Bearer aIcXSOoTtqrzR8L8YEIOmBeW94c3FmbSNSWAUbxsny9KKx5VFh",
    }

    @classmethod
    async def create(cls, client=None, main_request_timeout=10, json_loads=json.loads):
        if not client:
            main_request_timeout = aiohttp.ClientTimeout(main_request_timeout)
            import os
            headers = cls.DEFAULT_HEADERS.copy()
            if auth_override := os.environ.get("HYPERBLUR_TUMBLR_AUTHORIZATION"):
                if not auth_override.startswith("Bearer "):
                    auth_override = f"Bearer {auth_override}"
                headers["authorization"] = auth_override

            connector = aiohttp.TCPConnector(use_dns_cache=True, ttl_dns_cache=600, limit=300, limit_per_host=100, enable_cleanup_closed=True)
            client = aiohttp.ClientSession(
                "https://www.tumblr.com",
                headers=headers,
                timeout=main_request_timeout,
                connector=connector,
            )
        return cls(client, json_loads)

    def __init__(self, client: aiohttp.ClientSession, json_loads=json.loads):
        self.client = client
        self.json_loader = json_loads
        self._blog_post_cache = {}

    async def _get_json(self, endpoint, url_params=None):
        if url_params:
            url = f"{endpoint}?{urllib.parse.urlencode(url_params)}"
        else:
            url = f"{endpoint}"

        response = await self.client.get(f"/api/v2/{url}")

        try:
            result = await response.json(loads=self.json_loader)
        except Exception as e:
            if response.status != 200:
                raise TumblrNon200NorJSONResponse(response.status)
            logger.error(f"Failed to parse JSON response: {e}")
            raise InitialTumblrAPIParseException(getattr(e, "message", str(e)))

        if response.status == 429:
            raise TumblrRatelimitReachedError(response.status)
        elif response.status != 200:
            message = result.get("meta", {}).get("msg", "Error")
            code = result.get("meta", {}).get("status", response.status)

            if error := result.get("errors"):
                details = error[0].get("detail", "")
                internal_code = error[0].get("code")
            else:
                internal_code = None
                details = ""

            match internal_code:
                case 13001:
                    raise TumblrRestrictedTagError(message, code, details, internal_code)
                case 5029:
                    raise TumblrRatelimitReachedError(
                        response.status, response.headers.get("X-Rate-Limit-Reset")
                    )
                case 4012:
                    raise TumblrLoginRequiredError(message, code, details, internal_code)
                case 4013:
                    raise TumblrPasswordRequiredBlogError(message, code, details, internal_code)
                case 0:
                    raise TumblrBlogNotFoundError(message, code, details, internal_code)
                case _:
                    logger.error(f"Unknown tumblr internal error code: {internal_code}")
                    raise TumblrErrorResponse(message, code, details, internal_code)

        return result

    async def explore(self):
        return await self._get_json("explore")

    async def explore_trending(self, *, continuation: Optional[str] = None):
        url_parameters: dict = {"reblog_info": "true", "fields[blogs]": EXPLORE_BLOG_INFO_FIELDS}
        if continuation:
            url_parameters["cursor"] = continuation
        return await self._get_json("explore/trending", url_parameters)

    async def explore_today(self, *, continuation: Optional[str] = None):
        url_parameters = {
            "fields[blogs]": EXPLORE_BLOG_INFO_FIELDS,
            "reblog_info": "true",
        }
        if continuation:
            url_parameters["cursor"] = continuation
        return await self._get_json("explore/home/today", url_parameters)

    async def explore_post(
        self, post_type: ExplorePostTypeFilters, *, continuation: Optional[str] = None
    ):
        url_parameters: dict = {"reblog_info": "true", "fields[blogs]": EXPLORE_BLOG_INFO_FIELDS}
        if continuation:
            url_parameters["cursor"] = continuation
        return await self._get_json(f"explore/posts/{post_type.name.lower()}", url_parameters)

    async def timeline_search(
        self,
        query: str,
        timeline_type: TimelineType,
        *,
        continuation: Optional[str] = None,
        latest: bool = False,
        days: int = 0,
        post_type_filter: Optional[ExplorePostTypeFilters] = None,
    ):
        url_parameters = {
            "limit": 20,
            "days": days,
            "query": query,
            "mode": "top" if not latest else "recent",
        }
        if timeline_type == TimelineType.POST:
            url_parameters["timeline_type"] = "post"
            url_parameters["skip_component"] = "related_tags,blog_search"
        else:
            url_parameters["timeline_type"] = timeline_type.name.lower()

        url_parameters["reblog_info"] = "true"
        if post_type_filter:
            url_parameters["post_type_filter"] = post_type_filter.name.lower()
        url_parameters["fields[blogs]"] = TUMBLR_SEARCH_BLOG_INFO_FIELDS

        if continuation:
            url_parameters["cursor"] = continuation

        return await self._get_json("timeline/search", url_parameters)

    async def hubs_timeline(self, tag: str, *, continuation: Optional[str], latest: bool = False):
        url_parameters = {
            "fields[blogs]": TUMBLR_TAG_BLOG_INFO_FIELDS,
            "sort": "top" if not latest else "recent",
            "limit": 14,
        }
        if continuation:
            url_parameters["hub_name"] = tag
            url_parameters["rawurldecode"] = 1
            url_parameters["skip_header"] = 1
            url_parameters["cursor"] = continuation

        return await self._get_json(
            f"hubs/{urllib.parse.quote(tag, safe='')}/timeline", url_parameters
        )

    async def blog_posts(
        self, blog_name, continuation=None, tag=None, post_type=None, before_id=None
    ):
        url_parameters = {
            "fields[blogs]": BLOG_POSTS_BLOG_INFO_FIELDS,
            "npf": "true",
            "reblog_info": "true",
            "include_pinned_posts": "true",
        }
        if tag:
            url_parameters["tag"] = tag
            if post_type:
                url_parameters["post_type"] = post_type
        if before_id:
            url_parameters["before_id"] = before_id
        if continuation:
            url_parameters["tumblelog"] = blog_name
            url_parameters["page_number"] = continuation

        return await self._get_json(
            f"blog/{urllib.parse.quote(blog_name, safe='')}/posts", url_params=url_parameters
        )

    async def blog_search(
        self, blog_name, query, *, continuation=None, top=None, original_posts=None, post_type=None
    ):
        blog_name = urllib.parse.quote(blog_name, safe="")
        url_parameters = {
            "reblog_info": "true",
            "fields[blogs]": BLOG_SEARCH_BLOG_INFO_FIELDS,
            "npf": "true",
        }
        if post_type:
            url_parameters["post_type"] = post_type
        if original_posts:
            url_parameters["post_role"] = "ORIGINAL"
        if top:
            url_parameters["sort"] = "POPULARITY_DESC"
        else:
            url_parameters["sort"] = "CREATED_DESC"

        if continuation:
            url_parameters = url_parameters | {
                "tumblelog": blog_name,
                "query": query,
                "rawurldecode": 1,
                "cursor": continuation,
            }

        return await self._get_json(
            f"blog/{blog_name}/search/{urllib.parse.quote(query)}", url_params=url_parameters
        )

    async def blog_post(self, blog_name, post_id):
        cache_key = (blog_name, str(post_id))
        if cache_key in self._blog_post_cache:
            timestamp, result = self._blog_post_cache[cache_key]
            if time.time() - timestamp < 300:
                return result

        result = await self._get_json(
            f"blog/{urllib.parse.quote(blog_name, safe='')}/posts/{post_id}/permalink",
            url_params={"fields[blogs]": POST_BLOG_INFO_FIELDS, "reblog_info": "true"},
        )
        if len(self._blog_post_cache) > 500:
            self._blog_post_cache.clear()
        self._blog_post_cache[cache_key] = (time.time(), result)
        return result

    async def blog_post_replies(
        self, blog_id, post_id, latest: bool = False, after_id: Optional[str] = None
    ):
        if not after_id:
            url_parameters = {
                "mode": "replies",
                "sort": "desc" if latest else "asc",
                "pin_preview_note": "false",
                "fields[blogs]": "avatar,theme,name",
            }
        else:
            url_parameters = {"after": after_id, "sort": "desc" if latest else "asc"}

        return await self._get_json(
            f"blog/{urllib.parse.quote(blog_id, safe='')}/post/{post_id}/replies",
            url_params=url_parameters,
        )

    async def blog_post_notes_timeline(
        self,
        blog_id,
        post_id,
        mode: ReblogNoteTypes = ReblogNoteTypes.REBLOGS_WITH_COMMENTS,
        latest: bool = False,
        before_timestamp: Optional[str] = None,
    ):
        if before_timestamp:
            url_parameters = {
                "id": post_id,
                "mode": mode.name.lower(),
                "before_timestamp": before_timestamp,
            }
        else:
            url_parameters = {
                "mode": mode.name.lower(),
                "sort": "asc" if latest else "desc",
                "pin_preview_note": "false",
                "fields[blogs]": "avatar,theme,name",
            }

        return await self._get_json(
            f"blog/{urllib.parse.quote(blog_id, safe='')}/post/{post_id}/notes/timeline",
            url_params=url_parameters,
        )

    async def blog_notes(
        self,
        blog_id,
        post_id,
        latest: bool = True,
        return_likes: bool = True,
        before_timestamp: Optional[str] = None,
    ):
        if before_timestamp:
            url_parameters = {
                "mode": "likes" if return_likes else "reblogs_only",
                "id": post_id,
                "before_timestamp": before_timestamp,
            }
        else:
            url_parameters = {
                "id": post_id,
                "mode": "likes" if return_likes else "reblogs_only",
                "sort": "desc" if latest else "asc",
            }

        return await self._get_json(
            f"blog/{urllib.parse.quote(blog_id, safe='')}/notes", url_params=url_parameters
        )

    async def poll_results(self, blog_name, post_id, poll_id):
        return await self._get_json(
            f"polls/{urllib.parse.quote(blog_name, safe='')}/{post_id}/{poll_id}/results",
        )
