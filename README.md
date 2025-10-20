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

### Usage

```py
>>> from czkawka import ImageSimilarity
>>> finder = ImageSimilarity()
>>> finder.set_directories(["/path/to/images"])
>>> finder.set_similarity(15)  # 0-50, lower = stricter matching
>>> results = finder.find_similar()
[['image1.jpg', 'image1_copy.jpg'], ['photo.png', 'photo_edited.png']]
```

Refer to the [Czkawka docs](https://docs.rs/czkawka_core/latest/czkawka_core/) for all available options.

## Benchmarks

Benchmarks coming soon.

<!-- Tested with small and large image sets
- vs. [imagehash](https://pypi.org/project/imagehash): TBD
- vs. [PIL + manual comparison](https://pillow.readthedocs.io/): TBD -->

## Contributing

Maintained by [lmmx](https://github.com/lmmx). Contributions welcome!

1. **Issues & Discussions**: Please open a GitHub issue or discussion for bugs, feature requests, or questions.
2. **Pull Requests**: PRs are welcome!
   - Install the dev extra (e.g. with [uv](https://docs.astral.sh/uv/): `uv pip install -e .[dev]`)
   - Run tests (when available) and include updates to docs or examples if relevant.
   - If reporting a bug, please include the version and the error message/traceback if available.

## License

Licensed under the 2-Clause BSD License. See [LICENSE](https://github.com/lmmx/czkawka/blob/master/LICENSE) for all the details.
