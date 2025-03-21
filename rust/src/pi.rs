use pyo3::{exceptions::PyValueError, prelude::*};
use rand::{Rng, SeedableRng};

#[pyfunction]
pub fn pi_mc_rust(n_samples: u64, seed: u64) -> PyResult<f64> {
    if n_samples == 0 {
        return Err(PyValueError::new_err("n_samples must be positive"));
    }
    let mut rng = rand_pcg::Pcg64::seed_from_u64(seed);
    let mut count = 0;

    for _ in 0..n_samples {
        let x: f64 = rng.random();
        let y: f64 = rng.random();

        if x.powi(2) + y.powi(2) < 1.0 {
            count += 1
        }
    }

    let estimate = count as f64 / n_samples as f64 * 4.0;
    Ok(estimate)
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_pi_mc_rust() {
        let result = pi_mc_rust(10, 0).unwrap();
        assert!(result >= 0.0)
    }

    #[test]
    fn test_pi_mc_rust_zero() {
        assert!(pi_mc_rust(0, 0).is_err());
    }
}
