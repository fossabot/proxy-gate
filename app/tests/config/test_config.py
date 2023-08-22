"""
Test the Config class in config.py
"""
import json

import pytest
import yaml

from app.config import Config


class TestConfig:
    @pytest.fixture
    def mock_config_files(self, tmp_path):
        config_dir1 = tmp_path / "config_dir1"
        config_dir1.mkdir()

        # test-app-config.yaml is json but we don't support multiple
        # formats. YAML can still load json so its fine for now.
        config_file1 = config_dir1 / "test-app-config.yaml"
        config_file1.write_text(json.dumps({"key1": "valueWrong", "key2": "value2"}))

        config_dir2 = tmp_path / "config_dir2"
        config_dir2.mkdir()
        config_file2 = config_dir2 / "test-app-config.yaml"
        config_file2.write_text(yaml.dump({"key2": "valueWrong", "key3": "value3"}))

        return [config_dir1, config_dir2]

    def test_config_init(self, mock_config_files, monkeypatch):
        monkeypatch.setenv("TESTAPP_KEY1", "value1")
        monkeypatch.setattr(Config, "validate_config", lambda *args: None, raising=True)
        monkeypatch.setattr(
            Config, "load_from_defaults", lambda *args: {}, raising=True
        )
        config = Config(
            config_file_name="test-app-config.yaml",
            config_dirs=mock_config_files,
            env_prefix="TESTAPP",
            schema_name=None,
        )

        assert config.config == {
            "key1": "value1",
            "key2": "value2",
            "key3": "value3",
        }

        assert config("key1") == "value1"
        assert config("no-key") is None
