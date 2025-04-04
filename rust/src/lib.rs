mod pi;
mod two_level_system;

use pyo3::prelude::*;

#[pymodule]
mod _qpspin_mc {
    use super::*;

    #[pymodule]
    pub mod pi {
        #[pymodule_export]
        use crate::pi::pi_mc_rust;
    }

    #[pymodule]
    pub mod two_level_system {
        #[pymodule_export]
        use crate::two_level_system::tls_test_function;
    }
}

/*
Using (declarative module syntax)[https://pyo3.rs/main/module#declarative-modules].
The public interface of Python extension submodules is defined here, exposing objects
from the corresponding Rust modules.
They are then available as attributes of the main extension module, or can be imported
as submodules; but the object they expose cannot be imported directly.
For example
- `from qpspin_mc import _qpspin_mc`:
    - `_qpspin_mc` is bound as a module
    - `_qpspin_mc.pi` is bound as a module
    - `_qpspin_mc.pi.pi_mc_rust` is a function
- `from qpspin_mc._qpspin_mc import pi`:
    - `pi` is bound as a module
    - `pi.pi_mc_rust` is a function
but `from qpspin_mc._qpspin_mc.pi import pi_mc_rust` fails with
ModuleNotFoundError: No module named 'qpspin_mc._qpspin_mc.pi'; 'qpspin_mc._qpspin_mc' is not a package

Ideally, the Python submodule public interface would be declared in the Rust modules.
However we were able to set that up with imperative module syntax, but not with declarative.
This is how it worked:

```lib.rs
#[pymodule]
fn _qpspin_mc(m: &Bound<'_, PyModule>) -> PyResult<()> {
    let pi_module = crate::pi::init_module(m.py())?;
    m.add_submodule(&pi_module)?;

    Ok(())
}
```

```pi.rs
pub fn init_module<'py>(python: Python<'py>) -> PyResult<Bound<'py, PyModule>> {
    let pi_module = PyModule::new(python, "pi")?;
    pi_module.add_function(wrap_pyfunction!(pi_mc_rust, python)?)?;
    Ok(pi_module)
}
```

See also:
https://pyo3.rs/main/module
https://github.com/PyO3/pyo3/issues/759
https://github.com/PyO3/maturin/issues/266
https://github.com/PyO3/pyo3/issues/3900
*/
