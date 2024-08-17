from dataclasses import dataclass
import toml


with open("config.toml", "r") as config:
    config_data = toml.load(config)["Configuration"]

@dataclass(frozen=True)
class Information:
    folder: str = config_data["folder"]
    file: str = config_data["file"]
    output: str = config_data["output"]