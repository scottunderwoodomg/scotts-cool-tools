import json
from pathlib import Path


def load_config(config_path="config.json"):
    current_directory = script_dir = Path(__file__).resolve().parents[1]
    with open(f"{current_directory}/{config_path}", "r") as f:
        config = json.load(f)
    return config


def get_path(requested_path):
    return load_config()["local_paths"][requested_path]
