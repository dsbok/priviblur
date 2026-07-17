import os
import sys
import tomllib

from typing import NamedTuple, Union

from . import deployment, priviblur_backend, cache_config, user_preferences, logging_config, misc


class PriviblurConfig(NamedTuple):
    """NamedTuple storing configuration data for Priviblur

    Encapsulates various configuration settings under a single field.

    Attributes:
        deployment: Configuration settings for deploying Priviblur
        backend: Configuration settings to customize
            how Priviblur requests Tumblr
        logging: Configuration settings to change logging behavior
        misc: Configuration settings that doesn't fit into any other categories
    """

    deployment: deployment.DeploymentConfig
    backend: priviblur_backend.PriviblurBackendConfig
    default_user_preferences: user_preferences.DefaultUserPreferences
    cache: cache_config.CacheConfig
    logging: logging_config.LoggingConfig
    misc: misc.MiscellaneousConfig


def cast_val(val: str, field_type):
    # Unwrap Optional/Union
    origin = getattr(field_type, "__origin__", None)
    if origin is Union:
        args = getattr(field_type, "__args__", ())
        if args:
            non_none = [t for t in args if t is not type(None)]
            if non_none:
                field_type = non_none[0]
    elif hasattr(field_type, "__or__"):  # Python 3.10+ PEP 604 union type (e.g. str | None)
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


def load_config(path: str) -> PriviblurConfig:
    """Loads a TOML configuration file and environment variables into a PriviblurConfig object"""

    config = {}
    try:
        with open(path, "rb") as config_file:
            config = tomllib.load(config_file)
    except FileNotFoundError:
        # Optional config file, fall back to environment variables
        pass
    except PermissionError:
        print("Cannot access the configuration file. Do I have the right permissions?")
        sys.exit()

    # The config file can contain additional arguments that Priviblur does not recognize.
    # As such some processing is needed to only retrieve what Priviblur can understand

    # Defines config sections
    config_sections = (
        # Corresponding object, internal name, section name in the config file
        (deployment.DeploymentConfig, "deployment", "deployment"),
        (priviblur_backend.PriviblurBackendConfig, "backend", "priviblur_backend"),
        (
            user_preferences.DefaultUserPreferences,
            "default_user_preferences",
            "default_user_preferences",
        ),
        (cache_config.CacheConfig, "cache", "cache"),
        (logging_config.LoggingConfig, "logging", "logging"),
        (misc.MiscellaneousConfig, "misc", "misc"),
    )

    priviblur_config_data = {}

    for section_definition in config_sections:
        section_object, internal_name, external_name = section_definition
        arguments_to_load = {}
        arguments_from_config = config.get(external_name, {})

        # Ignore unknown config fields
        for k, v in arguments_from_config.items():
            if k in section_object._fields:
                arguments_to_load[k] = v

        # Load from environment variables
        for field_name in section_object._fields:
            # Format: PRIVIBLUR_[SECTION]_[KEY]
            env_var_name = f"PRIVIBLUR_{external_name.upper()}_{field_name.upper()}"
            env_val = os.environ.get(env_var_name)

            # Common fallbacks / aliases for ease of use in docker-compose
            if env_val is None and external_name == "deployment" and field_name == "host":
                env_val = os.environ.get("PRIVIBLUR_HOST")
            if env_val is None and external_name == "deployment" and field_name == "port":
                env_val = os.environ.get("PRIVIBLUR_PORT")
            if env_val is None and external_name == "cache" and field_name == "url":
                env_val = os.environ.get("REDIS_URL") or os.environ.get("PRIVIBLUR_REDIS_URL")

            if env_val is not None:
                field_type = section_object.__annotations__.get(field_name)
                try:
                    arguments_to_load[field_name] = cast_val(env_val, field_type)
                except Exception as e:
                    print(f"Error casting env var {env_var_name}={env_val} to {field_type}: {e}")

        priviblur_config_data[internal_name] = section_object(**arguments_to_load)

    # TODO Validate invalid config values

    return PriviblurConfig(**priviblur_config_data)
