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
from czkawka import ImageSimilarity

finder = ImageSimilarity()
finder.set_directories(["/path/to/images"])
finder.set_similarity(15)  # 0-50, lower = stricter matching

results = finder.find_similar()
# [['image1.jpg', 'image1_copy.jpg'], ['photo.png', 'photo_edited.png']]
```

What you get are groups of similar images, e.g. using the attached data we find the copies:
```py
>>> def find_similar(thresh: int):
...     finder = ImageSimilarity()
...     finder.set_directories(["tests/images"])
...     finder.set_similarity(thresh)
...     return finder.find_similar()
...
>>> pprint(find_similar(0))
[['/home/louis/dev/czkawka/tests/images/hello-world-white-fg-black-fg.png',
  '/home/louis/dev/czkawka/tests/images/hello-world-white-fg-black-fg_COPY.jpg',
  '/home/louis/dev/czkawka/tests/images/hello-world-white-fg-black-fg_COPY.png']]
```

Increasing the value from 0 to 50 doesn't make the first group it finds any bigger, it adds *more*
groups to the results. Each inner list is a cluster of images that are similar to each other.

### Hamming distances from clustering

You can also get **pairwise Hamming distances** between images in each cluster. The distances are bits changed between the perceptual hashes, so they are a discrete measure of distance (dissimilarity), with 0 being matching/duplicate images:
```python
from czkawka import ImageSimilarity

finder = ImageSimilarity()
finder.set_directories(["/path/to/images"])
finder.set_similarity(15)
results = finder.find_similar_with_distances()

# Returns: [
#   [('img1.jpg', 'img2.jpg', 0), ('img1.jpg', 'img3.jpg', 2)],
#   [('photo1.png', 'photo2.png', 5)]
# ]

for group in results:
    print("Similar image group:")
    for path_a, path_b, distance in group:
        print(f"  {path_a} ↔ {path_b}: {distance} bits different")
```

**Distance = 0** means identical perceptual hashes (perfect duplicates).
**Higher distances** mean less similar images.

Example:
```python
from pathlib import Path
from czkawka import ImageSimilarity

def find_similar_with_distances(thresh: int):
    finder = ImageSimilarity()
    finder.set_directories(["tests/images"])
    finder.set_similarity(thresh)
    return finder.find_similar_with_distances()

# Strict matching (distance = 0 means identical)
results = find_similar_with_distances(0)
for group in results:
    for a, b, d in group:
        print(f"{Path(a).name} ↔ {Path(b).name}: distance={d}")
```

Output:
```
hello-world-white-fg-black-fg.png ↔ hello-world-white-fg-black-fg_COPY.jpg: distance=0
hello-world-white-fg-black-fg.png ↔ hello-world-white-fg-black-fg_COPY.png: distance=0
hello-world-white-fg-black-fg_COPY.jpg ↔ hello-world-white-fg-black-fg_COPY.png: distance=0
```

### Direct distance computation between specific images

For more control, you can compute distances between specific images without running the clustering algorithm:
```python
from czkawka import ImageSimilarity

finder = ImageSimilarity()

images = [
    "photo1.jpg",
    "photo2.jpg",
    "photo3.jpg",
]

results = finder.compute_distances(images)
# Returns: [('photo1.jpg', 'photo2.jpg', 0), ('photo1.jpg', 'photo3.jpg', 14), ...]

for path_a, path_b, distance in results:
    print(f"{path_a} ↔ {path_b}: {distance}")
```

This computes all pairwise distances and returns them sorted by distance (most similar first). This is useful when you:
- Already know which images you want to compare
- Want distances without the clustering overhead
- Need fine-grained control over comparisons

Example output:
```python
>>> finder = ImageSimilarity()
>>> images = [
...     "tests/images/hello-world-white-fg-black-fg.png",
...     "tests/images/hello-world-white-fg-black-fg_COPY.png",
...     "tests/images/hello-world-white-fg-black-fg_SHRUNK.png",
... ]
>>> results = finder.compute_distances(images)
>>> for a, b, d in results:
...     print(f"{Path(a).name} ↔ {Path(b).name}: {d}")
...
hello-world-white-fg-black-fg.png ↔ hello-world-white-fg-black-fg_COPY.png: 0
hello-world-white-fg-black-fg.png ↔ hello-world-white-fg-black-fg_SHRUNK.png: 14
hello-world-white-fg-black-fg_COPY.png ↔ hello-world-white-fg-black-fg_SHRUNK.png: 14
```

### API Reference

- `ImageSimilarity()` - Create a new similarity finder
- `set_directories(paths: list[str])` - Set directories to search for clustering
- `set_similarity(level: int)` - Set similarity threshold (0-50, lower is stricter)
- `find_similar() -> list[list[str]]` - Find groups of similar images
- `find_similar_with_distances() -> list[list[tuple[str, str, int]]]` - Find groups with pairwise distances
- `compute_distances(paths: list[str]) -> list[tuple[str, str, int]]` - Compute distances between specific images

Refer to the [Czkawka docs](https://docs.rs/czkawka_core/latest/czkawka_core/) for more details on the underlying library.

## Benchmarks

Benchmarks coming soon.

## Contributing

Maintained by [lmmx](https://github.com/lmmx). Contributions welcome!

1. **Issues & Discussions**: Please open a GitHub issue or discussion for bugs, feature requests, or questions.
2. **Pull Requests**: PRs are welcome!
   - Install the dev extra (e.g. with [uv](https://docs.astral.sh/uv/): `uv pip install -e .[dev]`)
   - Run tests: `pytest tests/`
   - If reporting a bug, please include the version and the error message/traceback if available.

## License

Licensed under the 2-Clause BSD License. See [LICENSE](https://github.com/lmmx/czkawka/blob/master/LICENSE) for all the details.
