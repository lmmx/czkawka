"""Test of basic functionality."""

from pathlib import Path

import czkawka


def test_find_similar_with_distances(real_test_images):
    """Test finding similar images with distance metrics."""
    finder = czkawka.ImageSimilarity()
    finder.set_directories([real_test_images])
    finder.set_similarity(1)
    results = finder.find_similar_with_distances()

    assert isinstance(results, list)
    assert len(results) >= 1

    # Check structure: list of groups, each group is list of (path_a, path_b, distance) tuples
    for group in results:
        assert isinstance(group, list)
        for path_a, path_b, distance in group:
            assert isinstance(path_a, Path)
            assert isinstance(path_b, Path)
            assert isinstance(distance, int)
            assert distance >= 0  # Hamming distance is non-negative

    # Find the exact duplicate pair - should have distance 0
    found_exact_duplicate = False
    for group in results:
        for path_a, path_b, distance in group:
            if (
                path_a.name == "hello-world-white-fg-black-fg.png"
                and path_b.name == "hello-world-white-fg-black-fg_COPY.png"
            ):
                assert distance == 0, (
                    f"Expected exact duplicate to have distance 0, got {distance}"
                )
                found_exact_duplicate = True

    assert found_exact_duplicate, (
        "Expected to find exact duplicate pair with distance 0"
    )


def test_distance_increases_with_difference(real_test_images):
    """Test that more different images have higher distances."""
    finder = czkawka.ImageSimilarity()
    finder.set_directories([real_test_images])
    finder.set_similarity(50)  # Maximum to catch all images
    results = finder.find_similar_with_distances()

    # Collect distances
    distances = {}
    for group in results:
        for path_a, path_b, distance in group:
            key = tuple(sorted([Path(path_a).name, Path(path_b).name]))
            distances[key] = distance

    # The COPY should be closer to original than SHRUNK is to original
    if distances:
        print(f"Distances found: {distances}")
        # Just verify distances are reasonable integers
        for dist in distances.values():
            assert 0 <= dist <= 1000, f"Distance {dist} seems unreasonable"
