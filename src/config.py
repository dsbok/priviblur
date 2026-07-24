import os
import sys
import tomllib
from typing import NamedTuple, Optional, Union

class DeploymentConfig(NamedTuple):
    host: str = "0.0.0.0"
    port: int = 8000
    domain: Optional[str] = None
    https: bool = True


class HyperblurBackendConfig(NamedTuple):
    main_response_timeout: int = 10
    image_response_timeout: int = 30


class DefaultUserPreferences(NamedTuple):
    language: str = "en_US"
    theme: str = "auto"
    expand_posts: bool = False


class MiscellaneousConfig(NamedTuple):
    dev_mode: bool = False


class HyperblurConfig(NamedTuple):
    deployment: DeploymentConfig
    backend: HyperblurBackendConfig
    default_user_preferences: DefaultUserPreferences
    misc: MiscellaneousConfig


def cast_val(val: str, field_type):
    origin = getattr(field_type, "__origin__", None)
    if origin is Union or hasattr(field_type, "__or__"):
        args = getattr(field_type, "__args__", ())
        if args:
            non_none = [t for t in args if t is not type(None)]
            if non_none:
                field_type = non_none[0]

    if field_type is bool:
        return val.lower() in ("true", "1", "yes", "on")
    elif field_type is int:
        return int(val)
    return val


def load_config(path: str) -> HyperblurConfig:
    config = {}
    try:
        with open(path, "rb") as config_file:
            config = tomllib.load(config_file)
    except (FileNotFoundError, PermissionError):
        pass

    config_sections = (
        (DeploymentConfig, "deployment", "deployment"),
        (HyperblurBackendConfig, "backend", "hyperblur_backend"),
        (DefaultUserPreferences, "default_user_preferences", "default_user_preferences"),
        (MiscellaneousConfig, "misc", "misc"),
    )

    hyperblur_config_data = {}

    for section_object, internal_name, external_name in config_sections:
        arguments_to_load = {}
        arguments_from_config = config.get(external_name, {})

        for k, v in arguments_from_config.items():
            if k in section_object._fields:
                arguments_to_load[k] = v

        for field_name in section_object._fields:
            env_var_name = f"HYPERBLUR_{external_name.upper()}_{field_name.upper()}"
            env_val = os.environ.get(env_var_name)

            if env_val is None and external_name == "deployment" and field_name == "host":
                env_val = os.environ.get("HYPERBLUR_HOST")
            if env_val is None and external_name == "deployment" and field_name == "port":
                env_val = os.environ.get("HYPERBLUR_PORT")

            if env_val is not None:
                field_type = section_object.__annotations__.get(field_name)
                try:
                    arguments_to_load[field_name] = cast_val(env_val, field_type)
                except Exception:
                    pass

        hyperblur_config_data[internal_name] = section_object(**arguments_to_load)

    return HyperblurConfig(**hyperblur_config_data)
