"""Python wrapper for Czkawka image similarity detection with ergonomic APIs."""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

from ._czkawka import ImageSimilarity as _RustImageSimilarity

if TYPE_CHECKING:
    from collections.abc import Sequence

__version__ = "0.0.9"

__all__ = ["ImageSimilarity"]


class ImageSimilarity:
    """High-level interface for image similarity detection.

    This wraps the Rust implementation with a more Pythonic API, handling
    path conversion and providing cleaner type signatures.

    Examples
    --------
    Basic similarity search:

    >>> finder = ImageSimilarity()
    >>> finder.set_directories([Path("photos"), Path("downloads")])
    >>> finder.set_similarity(15)
    >>> groups = finder.find_similar()
    >>> for group in groups:
    ...     print(f"Found {len(group)} similar images")

    With Hamming distances:

    >>> finder = ImageSimilarity()
    >>> finder.set_directories([Path("images")])
    >>> results = finder.find_similar_with_distances()
    >>> for group in results:
    ...     for img_a, img_b, distance in group:
    ...         print(f"{img_a.name} ↔ {img_b.name}: {distance} bits")

    Direct distance computation:

    >>> finder = ImageSimilarity()
    >>> images = [Path("img1.jpg"), Path("img2.jpg"), Path("img3.jpg")]
    >>> distances = finder.compute_distances(images)
    >>> for a, b, d in distances:
    ...     print(f"{a.name} vs {b.name}: distance={d}")
    """

    def __init__(self) -> None:
        """Initialize a new image similarity finder."""
        self._inner = _RustImageSimilarity()

    def set_directories(self, paths: Sequence[str | Path]) -> None:
        """Configure directories to scan for similar images.

        Parameters
        ----------
        paths : Sequence[str | Path]
            Directory paths to search recursively for images

        Examples
        --------
        >>> finder = ImageSimilarity()
        >>> finder.set_directories([Path("~/photos"), "/data/images"])
        """
        str_paths = [str(Path(p).expanduser().resolve()) for p in paths]
        self._inner.set_directories(str_paths)

    def set_similarity(self, level: int) -> None:
        """Set the similarity threshold for matching.

        Parameters
        ----------
        level : int
            Similarity threshold from 0 to 50. Lower values require stricter
            matches (fewer bits different in perceptual hashes). A value of 0
            finds only identical images, while higher values find more loosely
            similar images.

        Examples
        --------
        >>> finder = ImageSimilarity()
        >>> finder.set_similarity(0)   # Only exact duplicates
        >>> finder.set_similarity(15)  # Moderately similar images
        >>> finder.set_similarity(30)  # Loosely similar images
        """
        if not 0 <= level <= 50:
            raise ValueError(f"Similarity level must be 0-50, got {level}")
        self._inner.set_similarity(level)

    def find_similar(self) -> list[list[Path]]:
        """Find groups of similar images in configured directories.

        Returns
        -------
        list[list[Path]]
            Groups of similar images, where each inner list contains paths
            to images that are visually similar to each other

        Examples
        --------
        >>> finder = ImageSimilarity()
        >>> finder.set_directories([Path("photos")])
        >>> finder.set_similarity(10)
        >>> groups = finder.find_similar()
        >>> for group in groups:
        ...     print(f"Similar images: {[p.name for p in group]}")
        """
        raw_groups = self._inner.find_similar()
        return [[Path(p) for p in group] for group in raw_groups]

    def find_similar_with_distances(
        self,
    ) -> list[list[tuple[Path, Path, int]]]:
        """Find similar images with pairwise Hamming distances.

        Returns
        -------
        list[list[tuple[Path, Path, int]]]
            Groups of similar images, where each group contains tuples of
            (path_a, path_b, hamming_distance). Distance of 0 means identical
            perceptual hashes. Results are sorted by distance within each group.

        Examples
        --------
        >>> finder = ImageSimilarity()
        >>> finder.set_directories([Path("images")])
        >>> finder.set_similarity(0)
        >>> results = finder.find_similar_with_distances()
        >>> for group in results:
        ...     for img_a, img_b, dist in group:
        ...         if dist == 0:
        ...             print(f"Exact duplicates: {img_a.name}, {img_b.name}")
        """
        raw_groups = self._inner.find_similar_with_distances()
        return [[(Path(a), Path(b), d) for a, b, d in group] for group in raw_groups]

    def compute_distances(
        self, paths: Sequence[str | Path]
    ) -> list[tuple[Path, Path, int]]:
        """Compute pairwise Hamming distances between specific images.

        This bypasses the clustering algorithm and directly computes distances
        between provided images. Useful when you already know which images to
        compare or want fine-grained control.

        Parameters
        ----------
        paths : Sequence[str | Path]
            Image file paths to compare

        Returns
        -------
        list[tuple[Path, Path, int]]
            Pairwise comparisons as (path_a, path_b, hamming_distance) tuples,
            sorted by distance (most similar first)

        Raises
        ------
        IOError
            If any image file cannot be loaded

        Examples
        --------
        >>> finder = ImageSimilarity()
        >>> images = [
        ...     Path("photo1.jpg"),
        ...     Path("photo1_edited.jpg"),
        ...     Path("photo2.jpg")
        ... ]
        >>> distances = finder.compute_distances(images)
        >>> for img_a, img_b, dist in distances:
        ...     print(f"{img_a.name} ↔ {img_b.name}: {dist} bits different")
        """
        str_paths = [str(Path(p).expanduser().resolve()) for p in paths]
        raw_results = self._inner.compute_distances(str_paths)
        return [(Path(a), Path(b), d) for a, b, d in raw_results]

    def hash_image(self, path: str | Path) -> str:
        """Compute perceptual hash for a single image.

        This returns the hash as a hex string that can be stored and compared
        later without re-hashing the image.

        Parameters
        ----------
        path : str | Path
            Image file path to hash

        Returns
        -------
        str
            Hexadecimal string representation of the perceptual hash

        Raises
        ------
        IOError
            If the image file cannot be loaded

        Examples
        --------
        >>> finder = ImageSimilarity()
        >>> hash1 = finder.hash_image(Path("photo.jpg"))
        >>> hash2 = finder.hash_image(Path("photo_copy.jpg"))
        >>> if hash1 == hash2:
        ...     print("Images are identical")
        """
        str_path = str(Path(path).expanduser().resolve())
        return self._inner.hash_image(str_path)

    def compare_hashes(self, hash1: str, hash2: str) -> int:
        """Compute Hamming distance between two perceptual hashes.

        Parameters
        ----------
        hash1 : str
            First hash (hex string from hash_image)
        hash2 : str
            Second hash (hex string from hash_image)

        Returns
        -------
        int
            Hamming distance (number of bits different)

        Examples
        --------
        >>> finder = ImageSimilarity()
        >>> hash1 = finder.hash_image(Path("photo.jpg"))
        >>> hash2 = finder.hash_image(Path("photo_edited.jpg"))
        >>> distance = finder.compare_hashes(hash1, hash2)
        >>> if distance == 0:
        ...     print("Exact duplicate")
        >>> elif distance < 10:
        ...     print("Very similar")
        """
        return self._inner.compare_hashes(hash1, hash2)
