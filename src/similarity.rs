use pyo3::prelude::*;
use std::path::PathBuf;
use std::sync::{Arc, atomic::AtomicBool};

use czkawka_core::tools::similar_images::{SimilarImages, SimilarImagesParameters};
use czkawka_core::common::traits::Search;
use czkawka_core::common::tool_data::CommonData;
use image_hasher::{HashAlg, FilterType};

/// Python wrapper for Czkawka's image similarity detection.
#[pyclass]
pub struct ImageSimilarity {
    inner: SimilarImages,
    directories: Vec<PathBuf>,  // Store directories so we can restore them
}

#[pymethods]
impl ImageSimilarity {
    #[new]
    fn new() -> Self {
        let params = SimilarImagesParameters::new(
            10,                          // similarity threshold
            8,                           // hash_size
            HashAlg::Gradient,           // hash algorithm
            FilterType::Lanczos3,        // image filter
            false,                       // exclude_images_with_same_size
            false,                       // ignore_hard_links
        );

        let mut inner = SimilarImages::new(params);

        // These configurations are required for the search to work
        inner.set_reference_directory(vec![]);
        inner.set_minimal_file_size(1);
        inner.set_use_cache(false);
        inner.set_recursive_search(true);

        Self {
            inner,
            directories: Vec::new(),
        }
    }

    /// Set directories to search for similar images.
    ///
    /// Args:
    ///     paths: List of directory paths to scan
    fn set_directories(&mut self, paths: Vec<String>) {
        let pathbufs: Vec<PathBuf> = paths.into_iter().map(PathBuf::from).collect();
        self.directories = pathbufs.clone();  // Store for later
        self.inner.set_included_directory(pathbufs);
    }

    /// Set similarity threshold for matching images.
    ///
    /// Args:
    ///     level: Similarity level (0-50). Lower values are stricter.
    fn set_similarity(&mut self, level: u32) {
        // Get old params
        let old_params = self.inner.get_params();

        // Create new params with updated similarity
        let new_params = SimilarImagesParameters::new(
            level,
            old_params.hash_size,
            old_params.hash_alg,
            old_params.image_filter,
            old_params.exclude_images_with_same_size,
            old_params.ignore_hard_links,
        );

        // Create new instance
        let mut new_inner = SimilarImages::new(new_params);

        // Re-apply all the required configurations
        new_inner.set_reference_directory(vec![]);
        new_inner.set_minimal_file_size(1);
        new_inner.set_use_cache(false);
        new_inner.set_recursive_search(true);

        // Restore the directories
        new_inner.set_included_directory(self.directories.clone());

        self.inner = new_inner;
    }

    /// Find groups of similar images in the configured directories.
    ///
    /// Returns:
    ///     List of groups, where each group contains paths to similar images.
    ///     Example: [['img1.jpg', 'img1_copy.jpg'], ['photo.png', 'photo2.png']]
    fn find_similar(&mut self) -> PyResult<Vec<Vec<String>>> {
        let stop_flag = Arc::new(AtomicBool::new(false));

        // Run the similarity search using the Search trait
        self.inner.search(&stop_flag, None);

        // Convert results to Python-friendly format
        let results = self.inner.get_similar_images();
        let py_results: Vec<Vec<String>> = results
            .iter()
            .map(|group| {
                group.iter()
                    .map(|entry| entry.path.to_string_lossy().to_string())
                    .collect()
            })
            .collect();

        Ok(py_results)
    }
}
