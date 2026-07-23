import functools
import typing
import babel.dates
import babel.numbers

# ponytail: embedded single-file English translations -> external i18n translation files & multi-locale data
TRANSLATIONS = {
    "en_US": {
        "project_title": "Hyperblur",
        "page_title_suffix": "- Hyperblur",
        "post_note_count": ("{0} note", "{0} notes"),
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
        "settings_theme_selector": "Theme",
        "settings_theme_selector_desc": "Select your display theme",
        "settings_theme_selector_option_auto": "Auto",
        "settings_theme_selector_option_light": "Light",
        "settings_theme_selector_option_dark": "Dark",
        "settings_save_changes": "Save Changes",
        "settings_cancel_changes": "Cancel",
        "settings_copy_as_bookmarklet": "Copy as bookmarklet",
        "settings_copy_as_bookmarklet_confirmed": "Copied",
        "settings_copy_as_bookmarklet_failed": "Unable to copy",
        "hyperblur_licences_page_title": "Licences",
        "post_note_viewer_view_replies_tab_title": "Replies",
        "post_note_viewer_view_reblogs_tab_title": "Reblogs",
        "post_note_viewer_view_likes_tab_title": "Likes",
        "post_note_viewer_view_reblogs_filter_reblogs_with_comments": "Comments and tags",
        "post_note_viewer_view_reblogs_filter_reblogs_with_content_comments": "Comments only",
        "post_note_viewer_view_reblogs_filter_reblogs_only": "Other reblogs",
        "post_note_viewer_view_replies_filter_sort_oldest": "Oldest first",
        "post_note_viewer_view_replies_filter_sort_newest": "Newest first",
        "settings_expand_blogger_truncated_posts": "Expand posts",
        "settings_expand_blogger_truncated_posts_desc": "Expands truncated posts automatically",
        "npf_renderer_asker_with_no_attribution": "Anonymous",
        "npf_renderer_asker_and_ask_verb": "{name} asked",
        "npf_renderer_unsupported_block_header": "Unsupported NPF block",
        "npf_renderer_unsupported_block_description": "Placeholder for the unsupported \"{block}\" type NPF block",
        "npf_renderer_generic_image_alt_text": "image",
        "npf_renderer_link_block_poster_alt_text": "Preview image for \"{site}\"",
        "npf_renderer_link_block_fallback_embeds_are_disabled": "Embeds are disabled",
        "npf_renderer_error_video_link_block_fallback_heading": "Error: unable to render video block",
        "npf_renderer_video_link_block_fallback_description": "Please click me to watch on the original site",
        "npf_renderer_error_link_block_fallback_native_video_player_non_tumblr_source": "Error: non-tumblr source for video player",
        "npf_renderer_fallback_audio_block_thumbnail_alt_text": "Album art",
        "npf_renderer_error_audio_link_block_fallback_heading": "Error: unable to render audio block",
        "npf_renderer_audio_link_block_fallback_description": "Please click me to listen on the original site",
        "npf_renderer_error_link_block_fallback_native_audio_player_non_tumblr_source": "Error: non-tumblr source for audio player",
        "npf_renderer_poll_total_votes": ("{votes} vote", "{votes} votes"),
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
}

EN_US_TRANSLATIONS = TRANSLATIONS["en_US"]
SUPPORTED_LANGUAGES = ["en_US"]


class NPFRendererStringsLocalizer:
    def __init__(self, language, translate_func):
        self.language = language
        self.translate_func = translate_func

    def translate(self, key, *args):
        return self.translate_func(self.language, f"npf_renderer_{key}", *args)

    def __getitem__(self, key: str):
        if key.startswith("plural_"):
            return lambda number: self.translate(key[7:], number)
        return self.translate(key)


class NPFRendererLocalizer:
    def __init__(self, language, translate_func) -> None:
        self.language = language
        self.strings_localizer = NPFRendererStringsLocalizer(language, translate_func)
        self.locale_formatting = {
            "duration": {"__default__": functools.partial(babel.dates.format_timedelta, threshold=1.1, locale=language)},
            "datetime": {"__default__": functools.partial(babel.dates.format_datetime, format="short", locale=language)},
            "decimal": {"__default__": functools.partial(babel.numbers.format_decimal, locale=language)},
        }

    def __getitem__(self, key: str):
        if key == "strings":
            return self.strings_localizer
        return self.locale_formatting


class Language:
    def __init__(self, locale) -> None:
        self.locale = locale
        self.npf_renderer_localizer = NPFRendererLocalizer(locale, translate)
        self.name, self.translation_percentage = "English", 100


def initialize_locales() -> typing.Mapping[str, Language]:
    return {locale: Language(locale) for locale in SUPPORTED_LANGUAGES}


def translate(
    language: str,
    id: str,
    number: int | float | None = None,
    substitution: str | dict | None = None,
) -> str:
    lang_dict = TRANSLATIONS.get(language, EN_US_TRANSLATIONS)
    raw_val = lang_dict.get(id)
    if raw_val is None:
        raw_val = EN_US_TRANSLATIONS.get(id, id)

    if isinstance(raw_val, (tuple, list)):
        index = 0 if (number == 1 or number == 1.0) else 1
        translated = raw_val[index] if len(raw_val) > index else raw_val[0]
    else:
        translated = str(raw_val)

    if isinstance(substitution, str):
        translated = translated.format(substitution)
    elif isinstance(substitution, dict):
        translated = translated.format(**substitution)
    elif number is not None and "{0}" in translated:
        translated = translated.format(number)

    return translated
