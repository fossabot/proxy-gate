# pylint: disable=too-few-public-methods
import json
import os
from pathlib import Path

import jsonschema
import yaml


class ConfigSingletonMeta(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super().__call__(*args, **kwargs)
        return cls._instances[cls]


class ConfigHandler:
    @staticmethod
    def set_config_files(config_dirs, config_file_name) -> list:
        config_files = []
        for config_dir in config_dirs:
            config_file = Path(config_dir) / config_file_name

            if config_file in config_files:
                raise ValueError(
                    f"Duplicate config dir entry found in {config_dir} in {config_dirs}"
                )

            if config_file.exists():
                config_files.append(config_file)
        return config_files

    @staticmethod
    def load_from_env(env_prefix, schema: dict = None) -> dict:
        if schema:
            valid_properties = get_property_names(schema)

        config = {}
        for env_var, value in os.environ.items():
            if env_var.startswith(env_prefix + "_"):
                key = env_var[len(env_prefix) + 1 :].lower()
                if schema and key not in valid_properties:
                    continue
                config[key] = value
        return config

    @staticmethod
    def load_from_defaults(schema_name: str) -> dict:
        data = {}
        schema_file = get_schema_file_path(schema_name)
        extend_json_with_defaults_in_schema(data, schema_file)
        return data

    @staticmethod
    def load_from_config_files(config_files: list) -> dict:
        data = {}
        config_files.reverse()
        for config_file in config_files:
            if config_file.suffix == ".json":
                with open(config_file, "r", encoding="utf-8") as file:
                    config_file_data = json.load(file)
            elif config_file.suffix == ".yaml":
                with open(config_file, "r", encoding="utf-8") as file:
                    config_file_data = yaml.safe_load(file)
            else:
                raise ValueError(f"Unknown config file type {config_file}")
            data.update(config_file_data)
        return data

    @staticmethod
    def validate_config(
        env_config: dict, file_config: dict, default_config: dict, schema_name: str
    ):
        configs = {
            "env": env_config,
            "file": file_config,
            "default": default_config,
        }
        for config_type, config in configs.items():
            try:
                validate_json(config, get_schema_file_path(schema_name))
            except Exception as ex:
                raise ValueError(f"Error while validating {config_type} config") from ex

    @staticmethod
    def time_duration_to_seconds(time_string):
        if time_string[-1] == "d":
            return int(time_string[:-1]) * 86400
        if time_string[-1] == "h":
            return int(time_string[:-1]) * 3600
        if time_string[-1] == "m":
            return int(time_string[:-1]) * 60
        if time_string[-1] == "w":
            return int(time_string[:-1]) * 7 * 86400

        return int(time_string)


class Config:
    """
    Provides an interface to configuration handling in order of precedence:
    1. Environment variables
    2. Config files in the order they are provided
    3. Defaults
    """

    def __init__(
        self,
        config_file_name,
        config_dirs,
        env_prefix,
        schema_name=None,
    ):
        self.config = {}
        if schema_name:
            schema = load_json(get_schema_file_path(schema_name))
        else:
            schema = None

        config_files = ConfigHandler.set_config_files(config_dirs, config_file_name)
        env_config = ConfigHandler.load_from_env(env_prefix, schema=schema)
        file_config = ConfigHandler.load_from_config_files(config_files)
        default_config = ConfigHandler.load_from_defaults(schema_name)
        ConfigHandler.validate_config(
            env_config, file_config, default_config, schema_name
        )
        self.config.update(default_config)
        self.config.update(file_config)
        self.config.update(env_config)

    def get(self, key):
        return self.config.get(key)

    __call__ = get


class ProxyGateConfig(Config, metaclass=ConfigSingletonMeta):
    def __init__(self):
        config_dirs = (
            [os.environ.get("PROXY_GATE_CONFIG_DIR")]
            if os.environ.get("PROXY_GATE_CONFIG_DIR")
            else []
        )
        super().__init__(
            "proxy-gate-config.yaml",
            config_dirs,
            "PROXY_GATE",
            "proxy-gate-config",
        )

        for _key in ["secret_key_validity", "secret_key_interim_validity"]:
            self.config[_key] = ConfigHandler.time_duration_to_seconds(
                self.config[_key]
            )


def load_json(json_file: Path):
    with open(json_file, "r", encoding="utf-8") as file_pointer:
        json_data = json.load(file_pointer)
    return json_data


def validate_json(json_data: dict, schema_file: Path):
    """
    Raises: jsonschema.exceptions.ValidationError if validation fails
    """
    schema = load_json(schema_file)

    jsonschema.validate(json_data, schema)
    return True


def get_schema_file_path(
    schema_name: str, schema_dir: str = Path(__file__).parent / "schemas"
):
    schema_file_name = schema_name + ".json"
    schema_file_path = schema_dir / schema_file_name
    if schema_file_path.exists():
        return schema_file_path

    raise FileNotFoundError(f"Schema file {schema_file_path} not found")


def init_default_set_validator(validator_class=jsonschema.Draft202012Validator):
    validate_properties = validator_class.VALIDATORS["properties"]

    def set_defaults(validator, properties, instance, schema):
        for _property, subschema in properties.items():
            if "default" in subschema:
                instance.setdefault(_property, subschema["default"])

        for error in validate_properties(
            validator,
            properties,
            instance,
            schema,
        ):
            yield error

    return jsonschema.validators.extend(
        validator_class,
        {"properties": set_defaults},
    )


def extend_json_with_defaults_in_schema(json_data: dict, schema_file: Path):
    schema = load_json(schema_file)
    DefaultValidatingValidator = init_default_set_validator()
    DefaultValidatingValidator(schema).validate(json_data)


def get_property_names(schema):
    property_names = []

    if "properties" in schema and isinstance(schema["properties"], dict):
        property_names.extend(schema["properties"].keys())

    if "items" in schema and isinstance(schema["items"], dict):
        property_names.extend(get_property_names(schema["items"]))

    if "allOf" in schema and isinstance(schema["allOf"], list):
        for sub_schema in schema["allOf"]:
            property_names.extend(get_property_names(sub_schema))

    if "anyOf" in schema and isinstance(schema["anyOf"], list):
        for sub_schema in schema["anyOf"]:
            property_names.extend(get_property_names(sub_schema))

    if "oneOf" in schema and isinstance(schema["oneOf"], list):
        for sub_schema in schema["oneOf"]:
            property_names.extend(get_property_names(sub_schema))

    return property_names
