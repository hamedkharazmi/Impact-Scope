#!/usr/bin/env python3
"""Test runner script for ImpactScope."""

import subprocess
import sys
from pathlib import Path


def main():
    """Run the test suite."""
    print("Running ImpactScope test suite...")

    # Check if we're in the right directory
    if not Path("pyproject.toml").exists():
        print("Error: pyproject.toml not found. Run from project root.")
        return 1

    # Install test dependencies if needed
    try:
        print("Installing test dependencies...")
        subprocess.run(
            ["uv", "sync", "--extra", "test"], check=True, capture_output=False
        )
    except subprocess.CalledProcessError as e:
        print(f"Failed to install test dependencies: {e}")
        return 1
    except FileNotFoundError:
        print("uv not found. Please install uv or run tests manually with pytest.")
        return 1

    # Run tests with coverage
    try:
        print("Running tests with coverage...")
        result = subprocess.run(
            [
                "uv",
                "run",
                "pytest",
                "--cov=src",
                "--cov-report=term-missing",
                "--cov-report=html:htmlcov",
                "tests/",
            ],
            capture_output=False,
        )

        if result.returncode == 0:
            print("All tests passed!")
            return 0
        else:
            print("Some tests failed.")
            return result.returncode

    except FileNotFoundError:
        print("uv not found. Please install uv or run tests manually with pytest.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
