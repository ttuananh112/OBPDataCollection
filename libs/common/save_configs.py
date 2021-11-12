import json


def save_config(folder_path, config):
    with open(f"{folder_path}/data_config.txt", "w", encoding="utf-8") as f:
        json.dump(config, f, ensure_ascii=False, indent=4)
