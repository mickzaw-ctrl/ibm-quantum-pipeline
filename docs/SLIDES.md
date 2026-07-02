# IBM Quantum Hybrid Test Pipeline - 12 Slides

## Slide 1: Title

```
┌─────────────────────────────────────────────────────────────────┐
│   🏛️  HYBRID QUANTUM TEST PIPELINE ARCHITECTURE                │
│              IBM QUANTUM                                        │
│   ┌───────────────┐    ┌───────────────┐    ┌───────────────┐  │
│   │   Qiskit Aer  │───▶│ IBM Cloud     │───▶│  Validation   │  │
│   │   (Local)     │    │ (Brisbane/    │    │  + Benchmark  │  │
│   │               │    │  Kyiv)        │    │               │  │
│   └───────────────┘    └───────────────┘    └───────────────┘  │
└─────────────────────────────────────────────────────────────────┘
```

## Slide 2: Pipeline Overview - 7 Steps + 3 Levels

```
LEVEL 3: VALIDATION + BENCHMARKING (QPU / Cloud)
     Step 7: PEC/ZNE Error Mitigation
     Step 6: Randomized Benchmarking
     Step 5: Quantum Volume Testing
                    ↓
LEVEL 2: IBM CLOUD (Real Hardware) (IBM Brisbane/Kyiv)
     Step 4: Deployment → QPU
     Step 3: Circuit Transpilation (IBM QASM)
                    ↓
LEVEL 1: LOCAL SIMULATOR (Qiskit Aer)
     Step 2: Noise Model Simulation
     Step 1: Quantum Circuit Design
```

## Slide 3: Level 1 - Qiskit Aer

Simulation types:
- statevector: Full state vector (no noise)
- density_matrix: Density matrix (noise models)
- stabilizer: Clifford circuits (fast)
- extended_stabilizer: Extended Clifford
- matrix_product_state: MPS for large circuits

## Slide 4: Step 1-2 - Circuit + Transpile

```python
from qiskit import QuantumCircuit

circuit = QuantumCircuit(2)
circuit.h(0)          # Hadamard
circuit.cx(0, 1)      # CNOT
circuit.measure_all()
```

Transpilation: Source gates → IBM basis gates (H, S, SX, X, Y, Z, CX, SWAP)

## Slide 5: Step 3-4 - Simulation + Verification

Depolarizing noise: ρ' = (1-p)ρ + p/3(XρX + YρY + ZρZ)

Fidelity thresholds:
- F > 0.99: Excellent
- F > 0.95: Good
- F > 0.90: Acceptable
- F < 0.90: Poor

## Slide 6: Level 2 - IBM Cloud

Backends:
- IBM Kyiv: 127 qubits, CNOT fid 99.2%, T1=300μs
- IBM Brisbane: 127 qubits, CNOT fid 99.5%, T1=250μs

```python
from qiskit_ibm_runtime import QiskitRuntimeService

service = QiskitRuntimeService()
backend = service.least_busy(n_qubits=127)
```

## Slide 7: Step 5-6 - Deployment + Measurements

Job types: qasm, real, simulator, auto

Empirical fidelity: F = (P(00) + P(11)) / 2

## Slide 8: Step 7A - PEC

Probabilistic Error Cancellation:
- Identify noisy operations
- Decompose to quasi-probabilities
- Sample inverse circuits
- Reweight and average

Σᵢ pᵢ E⁻¹ᵢ(ρ) = ρ (ideal)

## Slide 9: Step 7B - ZNE

Zero-Noise Extrapolation:
- Noise levels: [1.0, 1.5, 2.0, 2.5]
- Linear: F_ZNE = 2F₁ - F₂
- Quadratic: F_ZNE = 3F₁ - 3F₂ + F₃
- Exponential: F_ZNE = a·exp(-b·λ)

## Slide 10: Benchmarking

Randomized Benchmarking:
- F(m) = A + B·exp(-r·m)
- A = 1/d (baseline)
- AGF = 1 - (1-r)/d

Quantum Volume:
- QV = 2^(min(n_heavy, n_depth))
- IBM Kyiv: QV = 2^127 ≈ 10^38

## Slide 11: SHZSpin10 Connection

| Step | SHZSpin10 | IBM Quantum |
|------|-----------|-------------|
| 1 | Graph Design | Circuit Design |
| 2 | MC Simulation | Noise Model |
| 3 | Equilibrium | Transpile → QASM |
| 4 | Observables | QPU Deployment |
| 5 | Predictions | Measurements |
| 6 | Remedies | PEC/ZNE |
| 7 | Tests | Benchmarking |

## Slide 12: Summary

Testing Matrix (all ✓):
- n_s, r, f_NL, Λ, G_TT, 3-Gen

Next Steps:
- ✅ Local simulation (Qiskit Aer)
- ✅ Cloud deployment (IBM Brisbane/Kyiv)
- ✅ Error mitigation (PEC + ZNE)
- ⬜ Full benchmarking
- ⬜ SHZSpin10 circuits on real QPU
- ⬜ Cross-validation

---

**Thank you! Questions?**