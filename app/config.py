import os
from pathlib import Path
import yaml


class ProxyGateConfig:
    def __init__(self, config_file=None):
        self.config = {}
        self.config_file = self._set_config_file(config_file)
        self._load_config()

    def _set_config_file(self, config_file):
        if config_file is not None:
            return config_file
        elif os.environ.get("PROXY_GATE_CONFIG_DIR") is not None:
            return (
                Path(os.environ.get("PROXY_GATE_CONFIG_DIR")) / "proxy-gate-config.yml"
            )
        else:
            return None

    def _load_defaults(self):
        self.config["plex_auth_cookie_age"] = "31d"

    def _load_config(self):
        self._load_defaults()
        if self.config_file is not None and self.config_file.exists():
            with open(self.config_file, "r") as file:
                config_file_data = yaml.safe_load(file)
            self.config.update(config_file_data)
        self._load_calculated()

    def _load_calculated(self):
        self.config["plex_auth_cookie_age_seconds"] = self._convert_to_seconds(
            self.config["plex_auth_cookie_age"]
        )

    def _convert_to_seconds(self, time_string):
        if time_string[-1] == "d":
            return int(time_string[:-1]) * 86400
        elif time_string[-1] == "h":
            return int(time_string[:-1]) * 3600
        elif time_string[-1] == "m":
            return int(time_string[:-1]) * 60
        else:
            return int(time_string)
