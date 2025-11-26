#!/usr/bin/env python3
"""
Gamma API Presentation Generator

Creates presentations using Gamma's Generate API with proper polling and error handling.

Usage:
    # From stdin (JSON payload)
    python generate_presentation.py < payload.json

    # From heredoc
    python generate_presentation.py << 'EOF'
    {
        "inputText": "Your content",
        "textMode": "generate",
        "format": "presentation"
    }
    EOF

    # Run built-in example
    python generate_presentation.py --example
"""

import os
import sys
import time
import json
import select
from typing import Dict, Optional, Any
import requests

class GammaAPI:
    """Client for Gamma Generate API v1.0"""

    BASE_URL = "https://public-api.gamma.app/v1.0"

    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize Gamma API client.

        Args:
            api_key: Gamma API key. If not provided, reads from GAMMA_API_KEY env var.
        """
        self.api_key = api_key or os.environ.get("GAMMA_API_KEY")
        if not self.api_key:
            raise ValueError(
                "API key required. Provide via api_key parameter or GAMMA_API_KEY environment variable. "
                "Get your key from https://gamma.app/settings/api-keys"
            )

        self.headers = {"Content-Type": "application/json", "X-API-KEY": self.api_key}

    def create_generation(self, payload: Dict[str, Any]) -> str:
        """
        Create a new generation.

        Args:
            payload: Generation parameters (inputText, textMode, format, etc.)

        Returns:
            Generation ID

        Raises:
            requests.HTTPError: If request fails
        """
        url = f"{self.BASE_URL}/generations"

        response = requests.post(url, headers=self.headers, json=payload)
        response.raise_for_status()

        result = response.json()
        return result["generationId"]

    def get_generation(self, generation_id: str) -> Dict[str, Any]:
        """
        Get generation status and results.

        Args:
            generation_id: ID from create_generation

        Returns:
            Generation status and details

        Raises:
            requests.HTTPError: If request fails
        """
        url = f"{self.BASE_URL}/generations/{generation_id}"

        response = requests.get(url, headers=self.headers)
        response.raise_for_status()

        return response.json()

    def poll_until_complete(
        self,
        generation_id: str,
        poll_interval: int = 10,
        max_wait: int = 300,
        verbose: bool = True,
    ) -> Dict[str, Any]:
        """
        Poll generation until complete or timeout.

        Args:
            generation_id: Generation ID to poll
            poll_interval: Seconds between polls (default: 5)
            max_wait: Maximum seconds to wait (default: 300)
            verbose: Print status updates (default: True)

        Returns:
            Completed generation details

        Raises:
            TimeoutError: If generation doesn't complete within max_wait
            requests.HTTPError: If API request fails
        """
        start_time = time.time()

        while True:
            elapsed = time.time() - start_time

            if elapsed > max_wait:
                raise TimeoutError(
                    f"Generation did not complete within {max_wait} seconds"
                )

            result = self.get_generation(generation_id)
            status = result.get("status")

            if verbose:
                print(f"Status: {status} (elapsed: {int(elapsed)}s)", flush=True)

            if status == "completed":
                return result
            elif status == "failed":
                raise RuntimeError(f"Generation failed: {result}")
            elif status == "pending":
                time.sleep(poll_interval)
            else:
                raise ValueError(f"Unknown status: {status}")

    def generate_and_wait(
        self,
        payload: Dict[str, Any],
        poll_interval: int = 10,
        max_wait: int = 300,
        verbose: bool = True,
    ) -> Dict[str, Any]:
        """
        Create generation and wait for completion.

        Args:
            payload: Generation parameters
            poll_interval: Seconds between polls
            max_wait: Maximum seconds to wait
            verbose: Print status updates

        Returns:
            Completed generation with gammaUrl and optional pdfUrl/pptxUrl
        """
        if verbose:
            print("Creating generation...", flush=True)

        generation_id = self.create_generation(payload)

        if verbose:
            print(f"Generation ID: {generation_id}", flush=True)
            print("Polling for completion...", flush=True)

        result = self.poll_until_complete(
            generation_id,
            poll_interval=poll_interval,
            max_wait=max_wait,
            verbose=verbose,
        )

        return result


def has_stdin_data():
    """Check if there's data available on stdin without blocking"""
    # Check if stdin is a terminal (interactive)
    if sys.stdin.isatty():
        return False

    # For non-terminal stdin, check if data is available
    # This works on Unix-like systems
    try:
        return select.select([sys.stdin], [], [], 0.0)[0]
    except:
        # Fallback for Windows or if select fails
        # Assume data is available if not a tty
        return True


def run_example():
    """Run built-in example"""
    payload = {
        "inputText": "The future of renewable energy: solar, wind, and battery storage",
        "textMode": "generate",
        "format": "presentation",
        "numCards": 10,
        "textOptions": {
            "amount": "detailed",
            "tone": "professional, optimistic",
            "audience": "business leaders and investors",
        },
        "imageOptions": {"source": "aiGenerated", "style": "photorealistic, modern"},
    }
    return payload


def print_usage():
    """Print usage instructions"""
    print("Usage:", file=sys.stderr)
    print("  # From stdin (JSON payload)", file=sys.stderr)
    print("  python generate_presentation.py < payload.json", file=sys.stderr)
    print("", file=sys.stderr)
    print("  # From heredoc", file=sys.stderr)
    print("  python generate_presentation.py << 'EOF'", file=sys.stderr)
    print("  {", file=sys.stderr)
    print('      "inputText": "Your content",', file=sys.stderr)
    print('      "textMode": "generate",', file=sys.stderr)
    print('      "format": "presentation"', file=sys.stderr)
    print("  }", file=sys.stderr)
    print("  EOF", file=sys.stderr)
    print("", file=sys.stderr)
    print("  # Run built-in example", file=sys.stderr)
    print("  python generate_presentation.py --example", file=sys.stderr)


def main():
    """Main entry point"""

    # Determine payload source
    payload = None

    if len(sys.argv) > 1 and sys.argv[1] in ["--example", "-e"]:
        # Run built-in example
        print("Running built-in example...\n")
        payload = run_example()
    elif has_stdin_data():
        # Read JSON from stdin
        try:
            stdin_data = sys.stdin.read()
            payload = json.loads(stdin_data)
        except json.JSONDecodeError as e:
            print(f"Error: Invalid JSON from stdin: {e}", file=sys.stderr)
            sys.exit(1)
    else:
        # No input provided
        print("Error: No input provided", file=sys.stderr)
        print("", file=sys.stderr)
        print_usage()
        sys.exit(1)

    # Initialize API client (after determining we have valid payload request)
    try:
        client = GammaAPI()
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

    # Validate required fields
    required_fields = ["inputText", "textMode", "format"]
    missing_fields = [f for f in required_fields if f not in payload]
    if missing_fields:
        print(
            f"Error: Missing required fields: {', '.join(missing_fields)}",
            file=sys.stderr,
        )
        sys.exit(1)

    # Generate
    try:
        print("Starting generation...\n")

        result = client.generate_and_wait(payload, verbose=True)

        print("\n✅ Generation complete!")
        print(f"View in Gamma: {result['gammaUrl']}")

        if "pdfUrl" in result:
            print(f"PDF: {result['pdfUrl']}")
        if "pptxUrl" in result:
            print(f"PPTX: {result['pptxUrl']}")

        credits = result.get("credits", {})
        print(f"\nCredits used: {credits.get('deducted', 'N/A')}")
        print(f"Credits remaining: {credits.get('remaining', 'N/A')}")

    except requests.HTTPError as e:
        print(f"\n❌ API Error: {e}", file=sys.stderr)
        if e.response is not None:
            print(f"Response: {e.response.text}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
