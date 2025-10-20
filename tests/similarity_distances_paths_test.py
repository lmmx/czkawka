"""Test compute_distances functionality."""

from pathlib import Path

import czkawka
import pytest


def test_compute_distances_basic(real_test_images):
    """Test computing distances between specific images."""
    finder = czkawka.ImageSimilarity()

    images = [
        str(Path(real_test_images) / "hello-world-white-fg-black-fg.png"),
        str(Path(real_test_images) / "hello-world-white-fg-black-fg_COPY.png"),
        str(Path(real_test_images) / "hello-world-white-fg-black-fg_SHRUNK.png"),
    ]

    results = finder.compute_distances(images)
    print("\n=== Basic compute_distances (3 images) ===")
    for path_a, path_b, distance in results:
        print(f"{Path(path_a).name} ↔ {Path(path_b).name}: {distance}")

    assert isinstance(results, list)
    assert len(results) == 3  # 3 images = 3 pairs (C(3,2))

    # Check structure
    for path_a, path_b, distance in results:
        assert isinstance(path_a, Path)
        assert isinstance(path_b, Path)
        assert isinstance(distance, int)
        assert distance >= 0

    # Results should be sorted by distance
    distances = [d for _, _, d in results]
    assert distances == sorted(distances), "Results should be sorted by distance"


def test_compute_distances_exact_duplicates(real_test_images):
    """Test that exact duplicates have distance 0."""
    finder = czkawka.ImageSimilarity()

    images = [
        str(Path(real_test_images) / "hello-world-white-fg-black-fg.png"),
        str(Path(real_test_images) / "hello-world-white-fg-black-fg_COPY.png"),
    ]

    results = finder.compute_distances(images)
    print("\n=== Exact duplicates ===")
    for path_a, path_b, distance in results:
        print(f"{Path(path_a).name} ↔ {Path(path_b).name}: {distance}")

    assert len(results) == 1
    path_a, path_b, distance = results[0]
    assert distance == 0, (
        f"Expected exact duplicates to have distance 0, got {distance}"
    )


def test_compute_distances_different_images(real_test_images):
    """Test that different images have non-zero distance."""
    finder = czkawka.ImageSimilarity()

    images = [
        str(Path(real_test_images) / "hello-world-white-fg-black-fg.png"),
        str(Path(real_test_images) / "hello-world-black-fg-white-bg.png"),
    ]

    results = finder.compute_distances(images)
    print("\n=== Different images (inverted colors) ===")
    for path_a, path_b, distance in results:
        print(f"{Path(path_a).name} ↔ {Path(path_b).name}: {distance}")

    assert len(results) == 1
    path_a, path_b, distance = results[0]
    assert distance > 0, "Different images should have distance > 0"


def test_compute_distances_single_image(real_test_images):
    """Test that single image returns empty results."""
    finder = czkawka.ImageSimilarity()

    images = [
        str(Path(real_test_images) / "hello-world-white-fg-black-fg.png"),
    ]

    results = finder.compute_distances(images)
    print("\n=== Single image (should be empty) ===")
    print(f"Results: {results}")

    assert len(results) == 0, "Single image should produce no pairs"


def test_compute_distances_nonexistent_file(real_test_images):
    """Test error handling for nonexistent files."""
    finder = czkawka.ImageSimilarity()

    images = [
        str(Path(real_test_images) / "hello-world-white-fg-black-fg.png"),
        "/nonexistent/image.png",
    ]

    print("\n=== Nonexistent file (should raise error) ===")
    with pytest.raises(Exception):  # Should raise IOError
        results = finder.compute_distances(images)
        print(f"Unexpected success: {results}")


def test_compute_distances_all_test_images(real_test_images):
    """Test computing distances for all test images."""
    finder = czkawka.ImageSimilarity()

    test_dir = Path(real_test_images)
    images = [str(p) for p in test_dir.glob("*.png")]

    if len(images) < 2:
        pytest.skip("Need at least 2 images for this test")

    results = finder.compute_distances(images)
    print(f"\n=== All test images ({len(images)} images, {len(results)} pairs) ===")
    for path_a, path_b, distance in results:
        print(f"{Path(path_a).name} ↔ {Path(path_b).name}: {distance}")

    # n images should produce n*(n-1)/2 pairs
    expected_pairs = len(images) * (len(images) - 1) // 2
    assert len(results) == expected_pairs

    # Verify sorting by distance
    distances = [d for _, _, d in results]
    assert distances == sorted(distances)
