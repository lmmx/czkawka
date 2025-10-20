use pyo3::prelude::*;
use std::path::PathBuf;
use std::sync::{Arc, atomic::AtomicBool};

use czkawka_core::tools::similar_images::{SimilarImages, SimilarImagesParameters};
use czkawka_core::common::traits::Search;
use czkawka_core::common::tool_data::CommonData;
use image_hasher::{HashAlg, FilterType, HasherConfig};

/// Python wrapper for Czkawka's image similarity detection.
#[pyclass]
pub struct ImageSimilarity {
    inner: SimilarImages,
    directories: Vec<PathBuf>, // Store directories so we can restore them
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

    /// Find similar images and compute pairwise distances within each group.
    ///
    /// Returns:
    ///     List of groups, where each group contains tuples of (path_a, path_b, hamming_distance)
    ///     sorted by distance (most similar first).
    ///     Example: [[('img1.jpg', 'img2.jpg', 0), ('img1.jpg', 'img3.jpg', 2)], [...]]
    fn find_similar_with_distances(&mut self) -> PyResult<Vec<Vec<(String, String, u32)>>> {
        let stop_flag = Arc::new(AtomicBool::new(false));
        self.inner.search(&stop_flag, None);

        let groups = self.inner.get_similar_images();
        let params = self.inner.get_params();
        
        let hasher = HasherConfig::new()
            .hash_size(params.hash_size as u32, params.hash_size as u32)
            .hash_alg(params.hash_alg)
            .resize_filter(params.image_filter)
            .to_hasher();

        let mut result: Vec<Vec<(String, String, u32)>> = Vec::new();

        for group in groups {
            let mut hashes: Vec<(String, image_hasher::ImageHash)> = Vec::new();
            
            for entry in group {
                let path = entry.path.to_string_lossy().to_string();
                
                match image::open(&entry.path) {
                    Ok(img) => {
                        let hash = hasher.hash_image(&img);
                        hashes.push((path, hash));
                    }
                    Err(e) => {
                        eprintln!("Warning: couldn't load {}: {}", path, e);
                        continue;
                    }
                }
            }

            let mut pairs: Vec<(String, String, u32)> = Vec::new();
            for i in 0..hashes.len() {
                for j in (i + 1)..hashes.len() {
                    let distance = hashes[i].1.dist(&hashes[j].1);
                    pairs.push((
                        hashes[i].0.clone(),
                        hashes[j].0.clone(),
                        distance,
                    ));
                }
            }
            
            // Sort by distance (most similar first)
            pairs.sort_by_key(|(_a, _b, dist)| *dist);
            
            if !pairs.is_empty() {
                result.push(pairs);
            }
        }

        Ok(result)
    }
}
