import json
import sys

def load_devices(filename):
    """
    Load device inventory from a JSON file.
    Exits if the file does not exist or is invalid.
    """
    try:
        with open(filename, "r") as f:
            return json.load(f)

    except FileNotFoundError:
        sys.exit(f"ERROR: File '{filename}' not found.")

if __name__ == "__main__":
    main()