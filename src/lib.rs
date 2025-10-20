use pyo3::prelude::*;
use std::path::PathBuf;
use std::sync::{Arc, atomic::AtomicBool};

use czkawka_core::tools::similar_images::{SimilarImages, SimilarImagesParameters};
use czkawka_core::common::traits::Search;
use czkawka_core::common::tool_data::CommonData;
use image_hasher::{HashAlg, FilterType};

/// Python wrapper for Czkawka's image similarity detection.
#[pyclass]
struct ImageSimilarity {
    inner: SimilarImages,
}

#[pymethods]
impl ImageSimilarity {
    #[new]
    fn new() -> Self {
        // Use the new API with SimilarImagesParameters - all 6 fields required
        let params = SimilarImagesParameters::new(
            10,                          // similarity threshold
            8,                           // hash_size
            HashAlg::Gradient,           // hash algorithm
            FilterType::Lanczos3,        // image filter
            false,                       // exclude_images_with_same_size
            true,                        // ignore_hard_links
        );
        Self {
            inner: SimilarImages::new(params),
        }
    }

    /// Set directories to search for similar images.
    ///
    /// Args:
    ///     paths: List of directory paths to scan
    fn set_directories(&mut self, paths: Vec<String>) {
        let pathbufs: Vec<PathBuf> = paths.into_iter().map(PathBuf::from).collect();
        self.inner.set_included_directory(pathbufs);
    }

    /// Set similarity threshold for matching images.
    ///
    /// Args:
    ///     level: Similarity level (0-50). Lower values are stricter.
    fn set_similarity(&mut self, level: u32) {
        // Recreate SimilarImages with new similarity value
        let old_params = self.inner.get_params();
        let new_params = SimilarImagesParameters::new(
            level,
            old_params.hash_size,
            old_params.hash_alg,
            old_params.image_filter,
            old_params.exclude_images_with_same_size,
            old_params.ignore_hard_links,
        );
        self.inner = SimilarImages::new(new_params);
    }

    /// Find groups of similar images in the configured directories.
    ///
    /// Returns:
    ///     List of groups, where each group contains paths to similar images.
    ///     Example: [['img1.jpg', 'img1_copy.jpg'], ['photo.png', 'photo2.png']]
    fn find_similar(&mut self) -> PyResult<Vec<Vec<String>>> {
        // Create stop flag as required by v10 API
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

#[pymodule]
fn czkawka(m: &Bound<'_, PyModule>) -> PyResult<()> {
    // Expose the ImageSimilarity class
    m.add_class::<ImageSimilarity>()?;
    Ok(())
}
