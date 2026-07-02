# API Reference

## QuantumPipeline

Main class for the quantum test pipeline.

### Initialization

```python
from src.pipeline import QuantumPipeline

pipeline = QuantumPipeline(
    n_qubits=2,              # Number of qubits
    noise_level=0.01,        # 1-qubit gate error rate
    two_qubit_noise_level=0.02,  # 2-qubit gate error rate
    readout_error=0.02,      # Measurement error rate
    backend_name="aer_simulator"
)
```

### Methods

#### `create_bell_state() -> QuantumCircuit`
Create a Bell state circuit (2-qubit entangled state).

#### `create_ghz_state(n_qubits=None) -> QuantumCircuit`
Create GHZ state circuit.

#### `create_random_circuit(depth=3) -> QuantumCircuit`
Create random circuit for testing.

#### `transpile_circuit(circuit) -> QuantumCircuit`
Transpile circuit to IBM basis gates.

#### `simulate(circuit, shots=1000, use_noise=True) -> Dict`
Simulate circuit and return results.

#### `compute_fidelity(counts, circuit=None) -> float`
Compute empirical fidelity from counts.

#### `apply_zne(noise_levels, fidelities) -> float`
Apply Zero-Noise Extrapolation.

#### `apply_pec(circuit, shots=1000) -> float`
Apply Probabilistic Error Cancellation.

#### `run_benchmarking(n_sequences=10) -> Dict`
Run Randomized Benchmarking.

#### `run_full_pipeline(circuit, shots=5000) -> Dict`
Run complete 7-step pipeline.

---

## QuantumSimulator

Wrapper for Qiskit Aer.

```python
from src.simulator import QuantumSimulator

sim = QuantumSimulator(noise_model=my_noise)
```

### Methods

#### `run(circuit, shots=1000, method='automatic') -> Dict`
Run simulation with specified method.

#### `run_statevector(circuit) -> Statevector`
Run statevector simulation (no noise/measurements).

#### `run_stabilizer(circuit, shots=1000) -> Dict[str, int]`
Run stabilizer simulation for Clifford circuits.

#### `get_bloch_vector(circuit) -> np.ndarray`
Calculate Bloch vector for single qubit.

#### `get_fidelity(counts, target_state='00') -> float`
Calculate empirical fidelity.

---

## Noise Models

```python
from src.noise_model import (
    create_depolarizing_noise,
    create_thermal_noise,
    get_ibm_backend_noise_model,
)
```

### `create_depolarizing_noise()`
```python
noise = create_depolarizing_noise(
    one_qubit_error=0.001,
    two_qubit_error=0.01,
    readout_error=0.01,
    basis_gates=None  # Optional list
)
```

### `create_thermal_noise()`
```python
noise = create_thermal_noise(
    t1=100e-6,      # Relaxation time
    t2=100e-6,      # Dephasing time
    thermal_population=0.0,
    frequency=5e9
)
```

### `get_ibm_backend_noise_model()`
```python
noise = get_ibm_backend_noise_model(
    backend_name="ibm_kyiv",  # or "ibm_brisbane"
    gate_error_scale=1.0
)
```

---

## Fidelity

```python
from src.fidelity import (
    compute_state_fidelity,
    compute_empirical_fidelity,
    compute_bell_state_fidelity,
    compute_ghz_state_fidelity,
    fidelity_to_error_rate,
)
```

### `compute_state_fidelity(state1, state2, method='hilbert_schmidt') -> float`
Compute fidelity between two quantum states.

### `compute_empirical_fidelity(counts, target_states) -> float`
Compute empirical fidelity from measurement counts.

### `compute_bell_state_fidelity(counts) -> float`
Compute fidelity for Bell state: F = (P(00) + P(11)) / 2

### `fidelity_to_error_rate(fidelity, n_qubits=1) -> float`
Convert fidelity to error rate estimate.

---

## Error Mitigation

```python
from src.error_mitigation import (
    ZeroNoiseExtrapolation,
    ProbabilisticErrorCancellation,
    DynamicalDecoupling,
)
```

### ZeroNoiseExtrapolation

```python
zne = ZeroNoiseExtrapolation(method='linear')
f_zne = zne.extrapolate(noise_levels, fidelities)
```

### ProbabilisticErrorCancellation

```python
pec = ProbabilisticErrorCancellation(learning_rate=0.1)
pec.learn_noise_channel(circuit, backend, shots=1000)
f_pec = pec.apply(circuit, backend, shots=5000)
```

### DynamicalDecoupling

```python
dd = DynamicalDecoupling(sequence_type='xy4')
qc_with_dd = dd.apply(circuit)
```

---

## Benchmarking

```python
from src.benchmarking import (
    RandomizedBenchmarking,
    QuantumVolume,
    TomographyBenchmark,
)
```

### RandomizedBenchmarking

```python
rb = RandomizedBenchmarking(n_qubits=2)
results = rb.run(n_sequences=20, max_sequence_length=16)
print(f"AGF: {results['AGF']:.4f}")
```

### QuantumVolume

```python
qv = QuantumVolume()
result = qv.compute(n_qubits=5, depth=5)
print(f"QV = {result['QV']}")  # QV = 32
```

---

## Example Usage

### Complete Pipeline

```python
from src.pipeline import QuantumPipeline

# Create pipeline
pipeline = QuantumPipeline(n_qubits=2, noise_level=0.01)

# Create circuit
circuit = pipeline.create_bell_state()

# Run full pipeline
results = pipeline.run_full_pipeline(circuit, shots=5000)

# Access results
print(f"Fidelity: {results['simulation']['fidelity']:.4f}")
print(f"AGF: {results['benchmarking']['AGF']:.4f}")
```

### Error Mitigation

```python
# ZNE
zne = ZeroNoiseExtrapolation(method='exponential')
f_zne = zne.extrapolate(
    noise_levels=[1.0, 1.5, 2.0],
    fidelities=[0.98, 0.96, 0.94]
)
print(f"ZNE fidelity: {f_zne:.4f}")
```