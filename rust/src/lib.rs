mod pi;

use pyo3::prelude::*;

#[pymodule]
fn _qpspin_mc(m: &Bound<'_, PyModule>) -> PyResult<()> {
    #[pymodule]
    mod pi {
        use crate::pi::pi_mc_rust;
    }
    Ok(())
}
