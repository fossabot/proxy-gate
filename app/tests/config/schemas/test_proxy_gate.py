import jsonschema
import pytest

from app import config


class PropertyTest:
    """
    Class that can be used to perform tests on a property in a schema.
    """

    property_name = None

    def setup_method(self, method):
        print(f"Setting up test for {method.__name__}")

    def teardown_method(self, method):
        print(f"Tearing down test for {method.__name__}")


class EnumTest:
    """
    Provides methods for testing enum properties
    """

    property_name = None
    valid_enum_values = None
    invalid_enum_values = None

    def test_enum_valid_values(self):
        for valid_enum_values in self.valid_enum_values:
            test_config = {self.property_name: valid_enum_values}
            config.validate_json(
                test_config, config.get_schema_file_path("proxy-gate-config")
            )

    def test_enum_invalid_values(self):
        test_config = {self.property_name: self.invalid_enum_values}
        with pytest.raises(jsonschema.exceptions.ValidationError) as ex:
            config.validate_json(
                test_config, config.get_schema_file_path("proxy-gate-config")
            )

        assert "is not one of" in str(ex)


class TypeTest:
    def test_type_valid(self):
        test_config = {self.property_name: self.valid_type_value}
        config.validate_json(
            test_config, config.get_schema_file_path("proxy-gate-config")
        )

    def test_type_invalid(self):
        test_config = {self.property_name: self.invalid_type_value}
        with pytest.raises(jsonschema.exceptions.ValidationError) as ex:
            config.validate_json(
                test_config, config.get_schema_file_path("proxy-gate-config")
            )

        assert "is not of type" in str(ex)


class MinItemsTest:
    def test_min_items_valid(self):
        test_config = {self.property_name: self.valid_min_items}
        config.validate_json(
            test_config, config.get_schema_file_path("proxy-gate-config")
        )

    def test_min_items_invalid(self):
        test_config = {self.property_name: self.invalid_min_items}
        with pytest.raises(jsonschema.exceptions.ValidationError) as ex:
            config.validate_json(
                test_config, config.get_schema_file_path("proxy-gate-config")
            )

        assert f"{self.invalid_min_items} is too short" in str(ex)


class TestProperties:
    class TestAllowedAuthMethods(PropertyTest, EnumTest, TypeTest, MinItemsTest):
        property_name = "allowed_auth_methods"

        valid_enum_values = [["plex", "google"], ["google"], ["plex"]]
        invalid_enum_values = ["plex", "google", "this-should-not-work"]

        valid_type_value = valid_enum_values[0]
        invalid_type_value = "hello,how,are,you"

        valid_min_items = valid_enum_values[0]
        invalid_min_items = []

    class TestAppName(PropertyTest, TypeTest):
        property_name = "app_name"

        valid_type_value = "hello"
        invalid_type_value = 123


class TestSchemaValidation:
    class TestConfig:
        def test_empty_config(self):
            test_config = {}
            config.validate_json(
                test_config, config.get_schema_file_path("proxy-gate-config")
            )

        def test_additional_properties(self):
            test_config = {"the-added-property": "this-should-not-work"}
            with pytest.raises(jsonschema.exceptions.ValidationError) as ex:
                config.validate_json(
                    test_config, config.get_schema_file_path("proxy-gate-config")
                )

            assert "Additional properties are not allowed" in str(ex)
