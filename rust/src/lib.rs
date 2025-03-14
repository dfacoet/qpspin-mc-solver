use pyo3::prelude::*;

#[pyfunction]
#[allow(clippy::excessive_precision)]
fn pi_exact_rust() -> PyResult<f64> {
    let pi = 3.14159265358979323846; // more digits than f64 precision
    Ok(pi)
}

#[pymodule]
fn _qpspin_mc(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(pi_exact_rust, m)?)?;
    Ok(())
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_pi_exact_rust() {
        let result = pi_exact_rust().unwrap();
        assert_eq!(result, 3.14159265358979323846)
    }
}
