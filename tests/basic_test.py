"""Test of basic functionality."""

import shutil
import tempfile
from pathlib import Path

import pytest
from PIL import Image


@pytest.fixture
def temp_image_dir():
    """Create a temporary directory with test images."""
    tmpdir = tempfile.mkdtemp()

    # Create a simple test image
    img = Image.new("RGB", (100, 100), color="red")
    img.save(Path(tmpdir) / "image1.jpg")

    # Create a near-identical copy
    img2 = Image.new("RGB", (100, 100), color="red")
    img2.save(Path(tmpdir) / "image2.jpg")

    # Create a different image
    img3 = Image.new("RGB", (100, 100), color="blue")
    img3.save(Path(tmpdir) / "image3.jpg")

    yield tmpdir
    shutil.rmtree(tmpdir)


def test_basic_similarity(temp_image_dir):
    """Test finding similar images."""
    import czkawka

    finder = czkawka.ImageSimilarity()
    finder.set_directories([temp_image_dir])
    finder.set_similarity(15)
    results = finder.find_similar()

    assert isinstance(results, list)
    # Should find the two red images as similar
    assert len(results) >= 1


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
