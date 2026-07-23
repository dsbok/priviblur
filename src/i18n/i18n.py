import typing

from .i18n_data import LOCALE_DATA
from .npf_renderer_localizer import NPFRendererLocalizer
from .translations import TRANSLATIONS


class Language:
    """Stores metadata about supported translations"""

    def __init__(self, locale) -> None:
        self.locale = locale
        self.npf_renderer_localizer = NPFRendererLocalizer(locale, translate)
        self.name, self.translation_percentage = LOCALE_DATA.get(locale, ("English", 100))


SUPPORTED_LANGUAGES = [
    "en_US",
]

SUPPORTED_LANGUAGES.sort()


def initialize_locales() -> typing.Mapping[str, Language]:
    """Initializes locales using embedded translation dictionaries"""
    return {locale: Language(locale) for locale in SUPPORTED_LANGUAGES}


def translate(
    language: str,
    id: str,
    number: int | float | None = None,
    substitution: str | dict | None = None,
) -> str:
    lang_dict = TRANSLATIONS.get(language, TRANSLATIONS.get("en_US", {}))
    raw_val = lang_dict.get(id, TRANSLATIONS.get("en_US", {}).get(id, id))

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

