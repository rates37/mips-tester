"""
Utility functions for tests
"""

import requests
from pathlib import Path


def download_mars(mars_path: Path) -> None:
    """Downloads the mars jar file to a given path

    Args:
        mars_path (Path): The path to download the mars jar file to
    """
    url = "https://dpetersanderson.github.io/Mars4_5.jar"
    try:
        response = requests.get(url, stream=True)
        response.raise_for_status()
        with open(mars_path, "wb") as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        print(f"Mars JAR downloaded successfully to {mars_path}")
    except requests.exceptions.RequestException as e:
        print(f"Error downloading Mars JAR: {e}")
        raise
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        raise
