# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2024-01-XX

### Added

- **Core Pipeline**: Complete 7-step quantum test pipeline
  - Quantum circuit design
  - Noise model creation (depolarizing, thermal, custom)
  - Transpilation to IBM basis gates
  - Simulation with Qiskit Aer
  - Measurement collection and analysis
  - Error mitigation (ZNE, PEC, DD)
  - Benchmarking (RB, QV)

- **Simulator Module**: 
  - Multiple simulation methods (statevector, stabilizer, MPS)
  - Noise model integration
  - Bloch vector computation

- **Noise Models**:
  - Depolarizing noise with configurable error rates
  - Thermal noise (T1/T2 based)
  - IBM backend approximations (Kyiv, Brisbane)
  - Readout error modeling

- **Fidelity Computation**:
  - State fidelity (Hilbert-Schmidt, trace)
  - Process fidelity
  - Empirical fidelity from measurement counts
  - Bell state and GHZ state specific functions

- **Error Mitigation**:
  - Zero-Noise Extrapolation (linear, quadratic, exponential)
  - Probabilistic Error Cancellation
  - Dynamical Decoupling

- **Benchmarking**:
  - Randomized Benchmarking (RB) for AGF measurement
  - Quantum Volume computation
  - State tomography

- **Examples**:
  - Bell state generation and simulation
  - GHZ state generation
  - Random circuit testing

- **Documentation**:
  - README with quick start guide
  - API documentation
  - 12-slide presentation format
  - Test suite

### Features

- ✅ Local simulation (no cloud required)
- ✅ IBM Quantum cloud integration ready
- ✅ SHZSpin10 alignment (7-step schema)
- ✅ Error mitigation (PEC/ZNE)
- ✅ Benchmarking (RB/QV)

### Testing

- ✅ All 9 tests passing
- ✅ Circuit design tests
- ✅ Noise model tests
- ✅ Fidelity computation tests
- ✅ Full pipeline integration tests

## [0.1.0] - 2024-01-01

### Added

- Initial release with basic simulation capabilities
- Depolarizing noise model
- Bell state circuit generator