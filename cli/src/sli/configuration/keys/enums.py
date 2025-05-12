import enum


class ConfigKey:
    pass


class InternalConfigKey(ConfigKey, enum.Enum):
    """Internal Config Keys are not configurable by the user of the CLI."""

    CONFIG_MAIN_KEY = "SLI"
    CONFIG_VERSION = "config_version"


class ConfigurableConfigKey(ConfigKey, enum.Enum):
    pass

    def is_path(self) -> bool:
        return self.value.endswith("_path")

    def get_pleasant_name(self) -> str:
        return self.value.replace("_", " ")
