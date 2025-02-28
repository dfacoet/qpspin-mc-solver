use pyo3::prelude::*;

#[pyfunction]
fn pi_exact_rust() -> PyResult<f64> {
    let pi = 3.14159265358979323846; // more digits than f64 precision
    Ok(pi)
}

#[pymodule]
fn pi_rust(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(pi_exact_rust, m)?)?;
    Ok(())
}
