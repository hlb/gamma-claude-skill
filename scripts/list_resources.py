#!/usr/bin/env python3
"""
List available Gamma themes and folders.

Usage:
    python list_resources.py themes    # List all themes
    python list_resources.py folders   # List all folders
    python list_resources.py all       # List both
"""

import os
import sys
from typing import Dict, List, Any
import requests

class GammaResourceLister:
    """List Gamma workspace resources"""

    BASE_URL = "https://public-api.gamma.app/v1.0"

    def __init__(self, api_key: str = None):
        self.api_key = api_key or os.environ.get("GAMMA_API_KEY")
        if not self.api_key:
            raise ValueError(
                "API key required. Set GAMMA_API_KEY environment variable or pass api_key parameter. "
                "Get your key from https://gamma.app/settings/api-keys"
            )

        self.headers = {"X-API-KEY": self.api_key}

    def list_themes(self) -> List[Dict[str, Any]]:
        """List all available themes in workspace"""
        url = f"{self.BASE_URL}/themes"
        response = requests.get(url, headers=self.headers)
        response.raise_for_status()
        result = response.json()
        return result.get("data", [])

    def list_folders(self) -> List[Dict[str, Any]]:
        """List all available folders in workspace"""
        url = f"{self.BASE_URL}/folders"
        response = requests.get(url, headers=self.headers)
        response.raise_for_status()
        result = response.json()
        return result.get("data", [])

    def print_themes(self):
        """Print themes in readable format"""
        themes = self.list_themes()
        print("\n📐 Available Themes")
        print("=" * 60)

        for theme in themes:
            theme_id = theme.get("id", "N/A")
            name = theme.get("name", "Unnamed")
            is_default = theme.get("isDefault", False)

            default_marker = " [DEFAULT]" if is_default else ""
            print(f"• {name} (ID: {theme_id}){default_marker}")

            if "colors" in theme:
                colors = theme["colors"]
                print(
                    f"  Colors: Primary={colors.get('primary')}, Background={colors.get('background')}"
                )

        print("=" * 60)
        print(f"Total: {len(themes)} themes\n")

    def print_folders(self):
        """Print folders in readable format"""
        folders = self.list_folders()
        print("\n📁 Available Folders")
        print("=" * 60)

        for folder in folders:
            folder_id = folder.get("id", "N/A")
            name = folder.get("name", "Unnamed")

            print(f"• {name} (ID: {folder_id})")

        print("=" * 60)
        print(f"Total: {len(folders)} folders\n")


def main():
    if len(sys.argv) < 2:
        print("Usage: python list_resources.py [themes|folders|all]")
        sys.exit(1)

    command = sys.argv[1].lower()

    try:
        lister = GammaResourceLister()

        if command == "themes":
            lister.print_themes()
        elif command == "folders":
            lister.print_folders()
        elif command == "all":
            lister.print_themes()
            lister.print_folders()
        else:
            print(f"Unknown command: {command}")
            print("Usage: python list_resources.py [themes|folders|all]")
            sys.exit(1)

    except requests.HTTPError as e:
        print(f"❌ API Error: {e}", file=sys.stderr)
        if e.response is not None:
            print(f"Response: {e.response.text}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
