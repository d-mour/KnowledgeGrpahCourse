import json
import os
import sys


def load_json_data(directory, filename):
    """Load JSON data from a specified directory."""
    full_path = os.path.join(directory, filename)
    if not os.path.exists(full_path):
        print(f"Error: The file '{full_path}' does not exist.", file=sys.stderr)
        sys.exit(1)
    try:
        with open(full_path, "r") as f:
            return json.load(f)
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON from '{full_path}': {e}", file=sys.stderr)
        sys.exit(1)


def save_json_data(data: dict, directory: str, filename: str) -> None:
    """Saves dictionary data to a JSON file in the specified directory.

    Args:
        data: Dictionary containing data to save
        directory: Directory to save the file in
        filename: Name of the JSON file
    """
    os.makedirs(directory, exist_ok=True)
    filepath = os.path.join(directory, filename)
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
    print(f"Saved data to {filepath}")
