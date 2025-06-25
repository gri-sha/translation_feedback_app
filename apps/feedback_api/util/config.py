import json

_config = None

def get_config_db():
    global _config
    if _config is None:
        with open('config.json') as f:
            _config = json.load(f)["database"]
    print(f"Accessing db with configuration: {_config}")
    return _config