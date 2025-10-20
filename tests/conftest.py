"""Test of basic functionality."""

from pathlib import Path

import pytest


@pytest.fixture
def real_test_images():
    """Use the actual test images directory."""
    test_dir = Path(__file__).parent / "images"
    if not test_dir.exists():
        pytest.skip(f"Test images directory not found: {test_dir}")
    return str(test_dir)
