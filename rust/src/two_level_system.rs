use std::collections::HashSet;

use pyo3::prelude::*;

#[pyfunction]
pub fn tls_test_function(input_list: Vec<f64>) -> PyResult<(HashSet<u8>, Option<f64>)> {
    let mut set = HashSet::new();
    if let Some(first) = input_list.first() {
        if input_list.len() > 2 {
            set.extend([1, 1, 2, 3, first.round() as u8]);
        }
    }
    let sum = input_list.iter().sum();
    let maybe_float = if sum > 10.0 { Some(sum) } else { None };

    Ok((set, maybe_float))
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_tls_test_function() {
        for (input, expected_set, expected_maybe_float) in [
            (vec![], HashSet::new(), None),
            (vec![11.0], HashSet::new(), Some(11.0)),
            (vec![0.0, 1.0, 2.0], HashSet::from([1, 2, 3, 0]), None),
            (
                vec![0.0, 10.0, 2.0],
                HashSet::from([1, 2, 3, 0]),
                Some(12.0),
            ),
            (
                vec![1.0, 2.0, 3.0, 4.0, 5.0],
                HashSet::from([1, 2, 3]),
                Some(15.0),
            ),
            (vec![7.0, 2.0, 3.0], HashSet::from([1, 2, 3, 7]), Some(12.0)),
        ] {
            let (result_set, result_maybe_float) = tls_test_function(input).unwrap();
            assert_eq!(result_set, expected_set);
            assert_eq!(result_maybe_float, expected_maybe_float);
        }
    }
}
