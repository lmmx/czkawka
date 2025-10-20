use pyo3::prelude::*;

mod similarity;

use similarity::ImageSimilarity;

#[pymodule]
fn _czkawka(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_class::<ImageSimilarity>()?;
    Ok(())
}
