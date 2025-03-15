The goal of this project is to reimplement a continuous-time MC solver for impurity problems that arise in the study of phase diagrams of quantum p-spin models, as formulated in chapter 4 of my thesis [Facoetti (2019)](#citations).

For now, I'll play around with MCMC in Python and Rust.

# Development
## Setup
- Install [uv](https://docs.astral.sh/uv/)
- Build with `uv run maturin develop`
- Install pre-commit hooks `uv run pre-commit install`

uv takes care of creating a virtual environment and installing the Python and Rust packages with their dependencies, including development dependencies.

## Python
Use `uv run mypy` and `uv run ruff` to type check, lint and format (see pre-commit hooks).

For tests, `uv run pytest`.

## Rust
The project for the Rust extension module is at `rust/Cargo.toml`.

`cargo` should be rust from `rust`, or with `--manifest-path rust/Cargo.toml`.

To run Rust tests:

```
cargo test --no-default-features --manifest-path rust/Cargo.toml
```

The `--no-default-features` flag is needed to avoid [this known issue](https://pyo3.rs/v0.24.0/faq.html#i-cant-run-cargo-test-or-i-cant-build-in-a-cargo-workspace-im-having-linker-issues-like-symbol-not-found-or-undefined-reference-to-_pyexc_systemerror) with `maturin`, the `extension-module` feature and `cargo test` not playing nice together. We adopt solution 2.

Use `cargo fmt` and `cargo clippy` to format and lint (see pre-commit hooks).

## Citations

Facoetti, D. (2019). Ergodicity and Localisation in Mean-Field Quantum Systems [PhD thesis, King's College London]. https://kclpure.kcl.ac.uk/portal/en/studentTheses/ergodicity-and-localisation-in-mean-field-quantum-systems
