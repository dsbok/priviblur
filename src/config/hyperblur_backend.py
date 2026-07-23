from typing import NamedTuple


class HyperblurBackendConfig(NamedTuple):
    """NamedTuple that stores configuration values relating to Hyperblur Extractor

    Attributes:
        main_response_timeout: Timeout for API requests to Tumblr
        image_response_timeout: Timeout for media requests to Tumblr
    """

    main_response_timeout: int = 10
    image_response_timeout: int = 30
