"""Test hash_image and compare_hashes functionality."""

from pathlib import Path

import czkawka
import pytest


def test_hash_image_basic(real_test_images):
    """Test computing hash for a single image."""
    finder = czkawka.ImageSimilarity()

    image_path = Path(real_test_images) / "hello-world-white-fg-black-fg.png"
    hash_result = finder.hash_image(image_path)

    assert isinstance(hash_result, str)
    assert len(hash_result) > 0
    print(f"\nHash for {image_path.name}: {hash_result}")


def test_hash_image_consistency(real_test_images):
    """Test that hashing the same image twice produces the same hash."""
    finder = czkawka.ImageSimilarity()

    image_path = Path(real_test_images) / "hello-world-white-fg-black-fg.png"
    hash1 = finder.hash_image(image_path)
    hash2 = finder.hash_image(image_path)

    assert hash1 == hash2, "Same image should produce identical hashes"


def test_hash_image_accepts_string_path(real_test_images):
    """Test that hash_image accepts string paths."""
    finder = czkawka.ImageSimilarity()

    image_path = str(Path(real_test_images) / "hello-world-white-fg-black-fg.png")
    hash_result = finder.hash_image(image_path)

    assert isinstance(hash_result, str)
    assert len(hash_result) > 0


def test_hash_image_nonexistent_file(real_test_images):
    """Test error handling for nonexistent image file."""
    finder = czkawka.ImageSimilarity()

    nonexistent = Path(real_test_images) / "does_not_exist.png"

    with pytest.raises(IOError):
        finder.hash_image(nonexistent)


def test_compare_hashes_identical_images(real_test_images):
    """Test comparing hashes of identical images returns distance 0."""
    finder = czkawka.ImageSimilarity()

    img1 = Path(real_test_images) / "hello-world-white-fg-black-fg.png"
    img2 = Path(real_test_images) / "hello-world-white-fg-black-fg_COPY.png"

    hash1 = finder.hash_image(img1)
    hash2 = finder.hash_image(img2)

    distance = finder.compare_hashes(hash1, hash2)

    assert isinstance(distance, int)
    assert distance == 0, f"Identical images should have distance 0, got {distance}"
    print(f"\n{img1.name} ↔ {img2.name}: distance={distance}")


def test_compare_hashes_different_images(real_test_images):
    """Test comparing hashes of different images returns non-zero distance."""
    finder = czkawka.ImageSimilarity()

    img1 = Path(real_test_images) / "hello-world-white-fg-black-fg.png"
    img2 = Path(real_test_images) / "hello-world-black-fg-white-bg.png"

    hash1 = finder.hash_image(img1)
    hash2 = finder.hash_image(img2)

    distance = finder.compare_hashes(hash1, hash2)

    assert isinstance(distance, int)
    assert distance > 0, "Different images should have distance > 0"
    print(f"\n{img1.name} ↔ {img2.name}: distance={distance}")


def test_compare_hashes_same_hash(real_test_images):
    """Test comparing a hash with itself returns distance 0."""
    finder = czkawka.ImageSimilarity()

    img = Path(real_test_images) / "hello-world-white-fg-black-fg.png"
    hash_result = finder.hash_image(img)

    distance = finder.compare_hashes(hash_result, hash_result)

    assert distance == 0, "Same hash should have distance 0"


def test_compare_hashes_invalid_hash(real_test_images):
    """Test error handling for invalid hash strings."""
    finder = czkawka.ImageSimilarity()

    img = Path(real_test_images) / "hello-world-white-fg-black-fg.png"
    valid_hash = finder.hash_image(img)

    with pytest.raises(ValueError):
        finder.compare_hashes("invalid_hash", valid_hash)

    with pytest.raises(ValueError):
        finder.compare_hashes(valid_hash, "not_a_real_hash")


def test_hash_caching_workflow(real_test_images):
    """Test a realistic workflow: hash once, compare later without re-hashing."""
    finder = czkawka.ImageSimilarity()

    # Step 1: Hash original image and store it
    original = Path(real_test_images) / "hello-world-white-fg-black-fg.png"
    stored_hash = finder.hash_image(original)
    print(f"\nStored hash for {original.name}: {stored_hash}")

    # Step 2: Later, hash a generated/new image
    copy = Path(real_test_images) / "hello-world-white-fg-black-fg_COPY.png"
    new_hash = finder.hash_image(copy)
    print(f"New hash for {copy.name}: {new_hash}")

    # Step 3: Compare without re-loading the original
    distance = finder.compare_hashes(stored_hash, new_hash)

    if distance == 0:
        print("✓ Cache hit: generated image matches stored hash")
    else:
        print(f"✗ Cache miss: images differ by {distance} bits")

    assert distance == 0, "Copy should match original"


def test_hash_consistency_across_instances(real_test_images):
    """Test that different finder instances produce same hash."""
    img = Path(real_test_images) / "hello-world-white-fg-black-fg.png"

    finder1 = czkawka.ImageSimilarity()
    finder2 = czkawka.ImageSimilarity()

    hash1 = finder1.hash_image(img)
    hash2 = finder2.hash_image(img)

    assert hash1 == hash2, "Different instances should produce same hash"

    distance = finder1.compare_hashes(hash1, hash2)
    assert distance == 0


def test_multiple_image_hashing(real_test_images):
    """Test hashing multiple images and storing their hashes."""
    finder = czkawka.ImageSimilarity()

    test_dir = Path(real_test_images)
    images = list(test_dir.glob("*.png"))[:3]  # Just test first 3

    # Build a hash cache
    hash_cache = {}
    for img in images:
        hash_cache[img.name] = finder.hash_image(img)
        print(f"Cached {img.name}: {hash_cache[img.name]}")

    assert len(hash_cache) == len(images)
    assert all(isinstance(h, str) for h in hash_cache.values())

    # Compare all cached hashes
    print("\nPairwise distances from cached hashes:")
    img_names = list(hash_cache.keys())
    for i in range(len(img_names)):
        for j in range(i + 1, len(img_names)):
            dist = finder.compare_hashes(
                hash_cache[img_names[i]], hash_cache[img_names[j]]
            )
            print(f"{img_names[i]} ↔ {img_names[j]}: {dist}")
            assert dist >= 0


def test_hash_matches_compute_distances(real_test_images):
    """Test that manual hash comparison matches compute_distances results."""
    finder = czkawka.ImageSimilarity()

    img1 = Path(real_test_images) / "hello-world-white-fg-black-fg.png"
    img2 = Path(real_test_images) / "hello-world-white-fg-black-fg_COPY.png"

    # Method 1: Hash and compare manually
    hash1 = finder.hash_image(img1)
    hash2 = finder.hash_image(img2)
    manual_distance = finder.compare_hashes(hash1, hash2)

    # Method 2: Use compute_distances
    results = finder.compute_distances([img1, img2])
    assert len(results) == 1
    _, _, computed_distance = results[0]

    assert manual_distance == computed_distance, (
        f"Manual comparison ({manual_distance}) should match "
        f"compute_distances ({computed_distance})"
    )
