"""Test of basic functionality."""

import shutil
import tempfile
from pathlib import Path

import pytest


@pytest.fixture
def real_test_images():
    """Use the actual test images directory."""
    test_dir = Path(__file__).parent / "images"
    if not test_dir.exists():
        pytest.skip(f"Test images directory not found: {test_dir}")
    return str(test_dir)


def test_real_duplicate_images(real_test_images):
    """Test finding actual duplicate images in tests/images."""
    import czkawka

    finder = czkawka.ImageSimilarity()
    finder.set_directories([real_test_images])
    finder.set_similarity(1)  # Very strict - should catch exact duplicates
    results = finder.find_similar()

    assert isinstance(results, list)
    # Should find hello-world-white-fg-black-fg.png and its _COPY
    assert len(results) >= 1

    # Verify we found the copy pair
    found_copy = False
    for group in results:
        filenames = [Path(p).name for p in group]
        if (
            "hello-world-white-fg-black-fg.png" in filenames
            and "hello-world-white-fg-black-fg_COPY.png" in filenames
        ):
            found_copy = True
            break

    assert found_copy, f"Expected to find the COPY pair, got: {results}"


def test_similar_but_not_identical(real_test_images):
    """Test finding similar (but not identical) images."""
    import czkawka

    finder = czkawka.ImageSimilarity()
    finder.set_directories([real_test_images])
    finder.set_similarity(10)  # More lenient - should catch shrunk version
    results = finder.find_similar()

    assert isinstance(results, list)
    # Should potentially find shrunk version as similar
    # This test documents the behavior at similarity=10


def test_set_directories():
    """Test setting directories."""
    import czkawka

    finder = czkawka.ImageSimilarity()
    finder.set_directories(["/tmp"])
    # If it doesn't crash, it works


def test_set_similarity():
    """Test setting similarity levels."""
    import czkawka

    finder = czkawka.ImageSimilarity()
    finder.set_similarity(5)
    finder.set_similarity(25)
    finder.set_similarity(45)


def test_multiple_directories(real_test_images):
    """Test searching multiple directories at once."""
    import czkawka

    finder = czkawka.ImageSimilarity()
    finder.set_directories([real_test_images, real_test_images])
    results = finder.find_similar()

    assert isinstance(results, list)


def test_no_results_on_empty_dir():
    """Test that empty directory returns empty results."""
    import czkawka

    tmpdir = tempfile.mkdtemp()
    try:
        finder = czkawka.ImageSimilarity()
        finder.set_directories([tmpdir])
        results = finder.find_similar()

        assert isinstance(results, list)
        assert len(results) == 0
    finally:
        shutil.rmtree(tmpdir)


def test_nonexistent_directory():
    """Test behavior with non-existent directory."""
    import czkawka

    finder = czkawka.ImageSimilarity()
    finder.set_directories(["/nonexistent/path/that/does/not/exist"])
    results = finder.find_similar()

    # Should return empty results, not crash
    assert isinstance(results, list)
    assert len(results) == 0
