use pyo3::prelude::*;

#[pyfunction]
pub fn tls_test_function() -> PyResult<()> {
    Ok(())
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_tls_test_function() {
        let result = tls_test_function();
        assert!(result.is_ok());
    }
}
