#!/usr/bin/env rust-script
//! ```cargo
//! [dependencies]
//! czkawka_core = "10.0.0"
//! image_hasher = { version = "3.0.0", features = ["fast_image_resize", "fast_resize_unstable"] }
//! ```

use std::path::PathBuf;
use std::sync::{Arc, atomic::AtomicBool};

use czkawka_core::tools::similar_images::{SimilarImages, SimilarImagesParameters};
use czkawka_core::common::traits::Search;
use czkawka_core::common::tool_data::CommonData;
use image_hasher::{HashAlg, FilterType};

fn main() {
    println!("=== Czkawka Similar Images Test ===\n");

    // Create parameters with LOWER similarity threshold for testing
    let params = SimilarImagesParameters::new(
        1,                           // similarity threshold - VERY LOW for testing
        8,                           // hash_size
        HashAlg::Gradient,           // hash algorithm
        FilterType::Lanczos3,        // image filter
        false,                       // exclude_images_with_same_size
        false,                       // ignore_hard_links - FALSE to find copies
    );

    println!("Created SimilarImagesParameters:");
    println!("  - Similarity: {}", params.similarity);
    println!("  - Hash size: {}", params.hash_size);
    println!("  - Hash alg: {:?}", params.hash_alg);
    println!("  - Filter: {:?}", params.image_filter);

    // Create SimilarImages instance
    let mut similar_images = SimilarImages::new(params);
    println!("\nCreated SimilarImages instance");

    // Set directories to search (change this to your test directory)
    let test_dirs = vec![
        PathBuf::from("./tests/images"),  // Your directory with the hello-world images
    ];

    println!("\nSetting directories:");
    for dir in &test_dirs {
        println!("  - {}", dir.display());
        if !dir.exists() {
            println!("    WARNING: Directory does not exist!");
        } else if !dir.is_dir() {
            println!("    WARNING: Path exists but is not a directory!");
        } else {
            // List files in directory
            if let Ok(entries) = std::fs::read_dir(dir) {
                let files: Vec<_> = entries.filter_map(|e| e.ok()).collect();
                println!("    Found {} entries", files.len());
                for entry in files {
                    if let Ok(metadata) = entry.metadata() {
                        println!("      - {} ({} bytes)", entry.path().display(), metadata.len());
                    }
                }
            }
        }
    }
    similar_images.set_included_directory(test_dirs);

    // CRITICAL: Set minimum file size to 1 byte (default is 8192 bytes!)
    similar_images.set_minimal_file_size(1);

    // Enable recursive search
    similar_images.set_recursive_search(true);

    // Don't use cache for testing
    similar_images.set_use_cache(false);

    // Optional: Set excluded directories
    // similar_images.set_excluded_directory(vec![PathBuf::from("./excluded")]);

    // Set reference directories (required for search to work!)
    similar_images.set_reference_directory(vec![]);

    // Create stop flag
    let stop_flag = Arc::new(AtomicBool::new(false));

    println!("\nStarting search...");

    // Run the search
    similar_images.search(&stop_flag, None);

    println!("Search completed!\n");

    // Get results
    let similar_groups = similar_images.get_similar_images();

    println!("=== Results ===");
    println!("Found {} groups of similar images\n", similar_groups.len());

    if similar_groups.is_empty() {
        println!("No similar images found.");
        println!("\nTroubleshooting tips:");
        println!("  1. Make sure the directory exists and contains images");
        println!("  2. Try lowering the similarity threshold (currently 10)");
        println!("  3. Check file permissions");
    } else {
        for (i, group) in similar_groups.iter().enumerate() {
            println!("Group {}:", i + 1);
            for entry in group {
                println!("  - {} (size: {} bytes)",
                    entry.path.display(),
                    entry.size
                );
            }
            println!();
        }
    }

    // Additional diagnostics
    println!("=== Diagnostics ===");
    let info = similar_images.get_information();
    println!("Number of duplicates: {}", info.number_of_duplicates);
    println!("Number of groups: {}", info.number_of_groups);
}
