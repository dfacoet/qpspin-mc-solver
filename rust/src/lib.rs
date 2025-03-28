mod pi;

use pyo3::prelude::*;

/*
 // Option 1, this works
#[pymodule]
pub mod _qpspin_mc {
    use super::*;

    #[pymodule]
    pub mod pi {
        #[pymodule_export]
        pub use crate::pi::pi_mc_rust;

        #[pymodule_export]
        pub use crate::pi::joe_test;
    }
}
*/

#[pymodule]
fn _qpspin_mc(m: &Bound<'_, PyModule>) -> PyResult<()> {
    let pi_module = crate::pi::init_module(m.py())?;
    m.add_submodule(&pi_module)?;

    Ok(())
}
