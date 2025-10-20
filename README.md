# czkawka

<!-- [![downloads](https://static.pepy.tech/badge/czkawka/month)](https://pepy.tech/project/czkawka) -->
[![uv](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/uv/main/assets/badge/v0.json)](https://github.com/astral-sh/uv)
[![pdm-managed](https://img.shields.io/badge/pdm-managed-blueviolet)](https://pdm.fming.dev)
[![PyPI](https://img.shields.io/pypi/v/czkawka.svg)](https://pypi.org/project/czkawka)
[![Supported Python versions](https://img.shields.io/pypi/pyversions/czkawka.svg)](https://pypi.org/project/czkawka)
[![License](https://img.shields.io/pypi/l/czkawka.svg)](https://pypi.python.org/pypi/czkawka)
[![pre-commit.ci status](https://results.pre-commit.ci/badge/github/lmmx/czkawka/master.svg)](https://results.pre-commit.ci/latest/github/lmmx/czkawka/master)

Python bindings for the Czkawka Rust library, a fast image similarity engine

## Installation
```bash
pip install czkawka
```

### Requirements

- Python 3.9+

## Features

Fast image similarity in Rust, shipped for Python via PyO3.

Finds visually similar images regardless of resolution, format, or minor differences.

## Usage

### Image similarity clustering
```py
from pathlib import Path
from czkawka import ImageSimilarity

finder = ImageSimilarity()
finder.set_directories([Path("path/to/images")])
finder.set_similarity(15)  # 0-50, lower = stricter matching

results = finder.find_similar()
# Returns groups of Path objects:
# [[Path('image1.jpg'), Path('image1_copy.jpg')],
#  [Path('photo.png'), Path('photo_edited.png')]]
```

What you get are groups of similar images, e.g. using the attached data we find the copies:
```py
>>> from pathlib import Path
>>> def find_similar(thresh: int):
...     finder = ImageSimilarity()
...     finder.set_directories([Path("tests/images")])
...     finder.set_similarity(thresh)
...     return finder.find_similar()
...
>>> results = find_similar(0)
>>> for group in results:
...     print([p.name for p in group])
...
['hello-world-white-fg-black-fg.png',
 'hello-world-white-fg-black-fg_COPY.jpg',
 'hello-world-white-fg-black-fg_COPY.png']
```

Increasing the value from 0 to 50 doesn't make the first group it finds any bigger, it adds *more*
groups to the results. Each inner list is a cluster of images that are similar to each other.

### Hamming distances from clustering

You can also get **pairwise Hamming distances** between images in each cluster. The distances are bits changed between the perceptual hashes, so they are a discrete measure of distance (dissimilarity), with 0 being matching/duplicate images:
```python
from pathlib import Path
from czkawka import ImageSimilarity

finder = ImageSimilarity()
finder.set_directories([Path("path/to/images")])
finder.set_similarity(15)
results = finder.find_similar_with_distances()

# Returns groups with Path objects and distances:
# [
#   [(Path('img1.jpg'), Path('img2.jpg'), 0),
#    (Path('img1.jpg'), Path('img3.jpg'), 2)],
#   [(Path('photo1.png'), Path('photo2.png'), 5)]
# ]

for group in results:
    print("Similar image group:")
    for path_a, path_b, distance in group:
        print(f"  {path_a.name} ↔ {path_b.name}: {distance} bits different")
```

**Distance = 0** means identical perceptual hashes (perfect duplicates).
**Higher distances** mean less similar images.

Example:
```python
from pathlib import Path
from czkawka import ImageSimilarity

def find_similar_with_distances(thresh: int):
    finder = ImageSimilarity()
    finder.set_directories([Path("tests/images")])
    finder.set_similarity(thresh)
    return finder.find_similar_with_distances()

# Strict matching (distance = 0 means identical)
results = find_similar_with_distances(0)
for group in results:
    for a, b, d in group:
        print(f"{a.name} ↔ {b.name}: distance={d}")
```

Output:
```
hello-world-white-fg-black-fg.png ↔ hello-world-white-fg-black-fg_COPY.jpg: distance=0
hello-world-white-fg-black-fg.png ↔ hello-world-white-fg-black-fg_COPY.png: distance=0
hello-world-white-fg-black-fg_COPY.jpg ↔ hello-world-white-fg-black-fg_COPY.png: distance=0
```

### Hamming distances from file paths

For more control, you can compute distances between specific images without running the clustering algorithm:

```python
from pathlib import Path
from czkawka import ImageSimilarity

finder = ImageSimilarity()

images = [
    Path("photo1.jpg"),
    Path("photo2.jpg"),
    Path("photo3.jpg"),
]

results = finder.compute_distances(images)
# Returns: [(Path('photo1.jpg'), Path('photo2.jpg'), 0),
#           (Path('photo1.jpg'), Path('photo3.jpg'), 14), ...]

for path_a, path_b, distance in results:
    print(f"{path_a.name} ↔ {path_b.name}: {distance}")
```

This computes all pairwise distances and returns them sorted by distance (most similar first). This is useful when you:
- Already know which images you want to compare
- Want distances without the clustering overhead
- Need fine-grained control over comparisons

Example output:

```python
>>> from pathlib import Path
>>> from czkawka import ImageSimilarity
>>> finder = ImageSimilarity()
>>> images = [
...     Path("tests/images/hello-world-white-fg-black-fg.png"),
...     Path("tests/images/hello-world-white-fg-black-fg_COPY.png"),
...     Path("tests/images/hello-world-white-fg-black-fg_SHRUNK.png"),
... ]
>>> results = finder.compute_distances(images)
>>> for a, b, d in results:
...     print(f"{a.name} ↔ {b.name}: {d}")
...
hello-world-white-fg-black-fg.png ↔ hello-world-white-fg-black-fg_COPY.png: 0
hello-world-white-fg-black-fg.png ↔ hello-world-white-fg-black-fg_SHRUNK.png: 14
hello-world-white-fg-black-fg_COPY.png ↔ hello-world-white-fg-black-fg_SHRUNK.png: 14
```

### Perceptual hash caching

For maximum efficiency, you can compute and store perceptual hashes separately, then compare them later without re-loading images. This is ideal for snapshot testing or avoiding redundant hash computations:

```python
from pathlib import Path
from czkawka import ImageSimilarity

finder = ImageSimilarity()

# Compute hash once and store it (e.g., in a cache, database, or file)
original_hash = finder.hash_image(Path("source.jpg"))
print(f"Stored hash: {original_hash}")

# Later, hash a generated or new image
generated_hash = finder.hash_image(Path("generated.jpg"))

# Compare hashes without re-loading the original image
distance = finder.compare_hashes(original_hash, generated_hash)

if distance == 0:
    print("✓ Cache hit: images are identical")
else:
    print(f"✗ Cache miss: images differ by {distance} bits")
```

Use cases for hash caching:
- **Snapshot testing**: Store expected output hashes and validate generated images match
- **Deduplication**: Build a hash database to detect duplicates without storing full images
- **Incremental processing**: Cache hashes to avoid re-processing unchanged images
- **Distributed systems**: Share hashes between systems without transferring image files

Example workflow:

```python
>>> from pathlib import Path
>>> from czkawka import ImageSimilarity
>>> finder = ImageSimilarity()
>>>
>>> # Hash and cache multiple images
>>> cache = {}
>>> for img in Path("images").glob("*.png"):
...     cache[img.name] = finder.hash_image(img)
...
>>> # Later, compare a new image against the cache
>>> new_hash = finder.hash_image(Path("new_image.png"))
>>> for name, cached_hash in cache.items():
...     dist = finder.compare_hashes(new_hash, cached_hash)
...     if dist == 0:
...         print(f"Duplicate found: {name}")
```

### API Reference

- `ImageSimilarity()` - Create a new similarity finder
- `set_directories(paths: Sequence[str | Path])` - Set directories to search for clustering (accepts strings or Path objects)
- `set_similarity(level: int)` - Set similarity threshold (0-50, lower is stricter)
- `find_similar() -> list[list[Path]]` - Find groups of similar images
- `find_similar_with_distances() -> list[list[tuple[Path, Path, int]]]` - Find groups with pairwise distances
- `compute_distances(paths: Sequence[str | Path]) -> list[tuple[Path, Path, int]]` - Compute distances between specific images
- `hash_image(path: str | Path) -> str` - Compute perceptual hash for a single image (returns base64 string)
- `compare_hashes(hash1: str, hash2: str) -> int` - Compare two perceptual hashes and return Hamming distance

All methods that return paths now return `pathlib.Path` objects instead of strings, providing better type safety and easier path manipulation.

Refer to the [Czkawka docs](https://docs.rs/czkawka_core/latest/czkawka_core/) for more details on the underlying library.

## Benchmarks

Benchmarks to be determined... (TODO).

## Contributing

Maintained by [lmmx](https://github.com/lmmx). Contributions welcome!

1. **Issues & Discussions**: Please open a GitHub issue or discussion for bugs, feature requests, or questions.
2. **Pull Requests**: PRs are welcome!
   - Install the dev extra (e.g. with [uv](https://docs.astral.sh/uv/): `uv pip install -e .[dev]`)
   - Run tests: `pytest tests/`
   - If reporting a bug, please include the version and the error message/traceback if available.

## License

Licensed under the MIT License. See [LICENSE](https://github.com/lmmx/czkawka/blob/master/LICENSE).
