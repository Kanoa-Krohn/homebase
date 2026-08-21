import os
import json

CACHE_DIR = os.path.join(os.path.dirname(__file__), '..', 'cache')


def save_cache(name, data):
    os.makedirs(CACHE_DIR, exist_ok=True)
    with open(os.path.join(CACHE_DIR, f'{name}.json'), 'w') as f:
        json.dump(data, f)


def load_cache(name):
    try:
        with open(os.path.join(CACHE_DIR, f'{name}.json')) as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return None