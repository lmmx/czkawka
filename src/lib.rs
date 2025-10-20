use pyo3::prelude::*;

mod similarity;

use similarity::ImageSimilarity;

#[pymodule]
fn czkawka(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_class::<ImageSimilarity>()?;
    Ok(())
}