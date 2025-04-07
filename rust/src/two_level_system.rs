use std::{collections::HashSet, f64};

use pyo3::prelude::*;
use rand::{Rng, SeedableRng, seq::IteratorRandom};

const _P_ADD: f64 = 0.5;

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

type TwoLevelSystemSample = Vec<f64>;

#[pyfunction]
pub fn run_mc(
    gamma: f64,
    h: f64,
    beta: f64,
    n_init_steps: u64,
    n_samples: u64,
    n_thinning: u64,
    seed: u64,
) -> PyResult<(Vec<TwoLevelSystemSample>, u64)> {
    let mut rng = rand_pcg::Pcg64::seed_from_u64(seed);
    let mut samples = Vec::new();
    let mut n_accepted = 0;
    let mut state = TwoLevelSystemSample::new();

    for _ in 0..n_init_steps {
        (state, _) = step(&state, gamma, h, beta, &mut rng);
    }

    for _ in 0..n_samples {
        for _ in 0..n_thinning {
            let (new_state, acc) = step(&state, gamma, h, beta, &mut rng);
            if acc {
                state = new_state;
                n_accepted += 1;
            }
        }
        samples.push(state.clone());
    }

    Ok((samples, n_accepted))
}

enum MoveType {
    Add,
    Remove,
}

// Figure out type bounds for rng
fn step(
    state: &TwoLevelSystemSample,
    gamma: f64,
    h: f64,
    beta: f64,
    rng: &mut rand_pcg::Pcg64,
) -> (TwoLevelSystemSample, bool) {
    let mut new_ts = state.clone();
    let prop_ratio = if state.is_empty() || rng.random::<f64>() < _P_ADD {
        let two_ts = vec![rng.random::<f64>() * beta, rng.random::<f64>() * beta];
        new_ts.extend(two_ts);
        // floats are not totally ordered.
        // Fails with NaNs, but state is guaranteed to only contain numbers
        new_ts.sort_by(|a, b| a.partial_cmp(b).unwrap());
        proposal_ratio(beta, state.len(), MoveType::Add)
    } else {
        // Remove two times from the state (uniform random)
        for _ in 0..2 {
            let index = (0..new_ts.len())
                .choose(rng)
                .expect("Trying to remove times from an empty state");
            new_ts.remove(index);
        }
        proposal_ratio(beta, state.len(), MoveType::Remove)
    };

    let p = compute_weight(&new_ts, gamma, h, beta) / compute_weight(state, gamma, h, beta)
        * prop_ratio;
    let accept = rng.random::<f64>() < p;
    (new_ts, accept)
}

fn proposal_ratio(beta: f64, two_l: usize, move_type: MoveType) -> f64 {
    // TODO: compute beta.powi(2) once
    match (two_l, move_type) {
        (0, MoveType::Add) => beta.powi(2) / 4.0,
        (2, MoveType::Remove) => 4.0 / beta.powi(2),
        (_, MoveType::Add) => beta.powi(2) / (((two_l + 2) * (two_l + 1)) as f64),
        (_, MoveType::Remove) => ((two_l * (two_l - 1)) as f64) / beta.powi(2),
    }
}

fn compute_weight(state: &TwoLevelSystemSample, gamma: f64, h: f64, beta: f64) -> f64 {
    let alternating_sum: f64 = state
        .iter()
        .enumerate()
        .map(|(k, t)| *t * ((2 * (k % 2)) as f64 - 1.0))
        .sum();

    2.0 * gamma.powi(state.len() as i32) * (h * (beta + 2.0 * alternating_sum)).cosh()
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
