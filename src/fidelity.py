"""
Fidelity Computation Module
===========================

Functions for computing quantum state and process fidelities.

Author: Michał Ślusarczyk
Version: 1.0.0
"""

from typing import Dict, List, Optional, Tuple, Union
import numpy as np
from qiskit import QuantumCircuit
from qiskit.quantum_info import Statevector, DensityMatrix, Operator
from qiskit.quantum_info.analyze import gate_error


def compute_state_fidelity(
    state1: Union[Statevector, np.ndarray],
    state2: Union[Statevector, np.ndarray],
    method: str = "hilbert_schmidt",
) -> float:
    """
    Compute fidelity between two quantum states.
    
    F = |⟨ψ₁|ψ₂⟩|² for pure states
    F = (Tr[√√ρ₁ρ₂√ρ₁])² for mixed states
    
    Args:
        state1: First state (statevector or density matrix)
        state2: Second state
        method: "hilbert_schmidt" or "trace"
    
    Returns:
        Fidelity value (0-1)
    """
    if isinstance(state1, np.ndarray):
        state1 = Statevector(state1)
    if isinstance(state2, np.ndarray):
        state2 = Statevector(state2)
    
    if method == "hilbert_schmidt":
        # Hilbert-Schmidt inner product
        overlap = np.abs(np.vdot(state1.data, state2.data))**2
        return float(overlap)
    
    elif method == "trace":
        # Trace distance method
        dm1 = DensityMatrix(state1)
        dm2 = DensityMatrix(state2)
        
        # sqrt of product
        sqrt_rho = dm1.power(0.5)
        product = sqrt_rho @ dm2 @ sqrt_rho
        sqrt_product = product.power(0.5)
        
        return float(np.real(np.trace(sqrt_product)))
    
    else:
        raise ValueError(f"Unknown method: {method}")


def compute_process_fidelity(
    circuit1: QuantumCircuit,
    circuit2: QuantumCircuit,
) -> float:
    """
    Compute process fidelity between two circuits.
    
    Args:
        circuit1: First circuit (ideal)
        circuit2: Second circuit (noisy)
    
    Returns:
        Process fidelity
    """
    # Get unitary operators
    try:
        op1 = Operator(circuit1)
        op2 = Operator(circuit2)
        
        # Compute process fidelity
        product = op1.adjoint() @ op2
        fidelity = np.abs(np.trace(product.data)) / product.dim[0]
        
        return float(fidelity)
    except Exception:
        return 0.0


def compute_empirical_fidelity(
    counts: Dict[str, int],
    target_states: List[str],
) -> float:
    """
    Compute empirical fidelity from measurement counts.
    
    F = Σ P(|target_i⟩) / |targets|
    
    Args:
        counts: Measurement counts {"00": 450, "01": 25, ...}
        target_states: List of target states, e.g., ["00", "11"]
    
    Returns:
        Empirical fidelity (0-1)
    """
    total = sum(counts.values())
    if total == 0:
        return 0.0
    
    target_count = sum(counts.get(state, 0) for state in target_states)
    
    return target_count / total


def compute_fidelity_with_noise(
    ideal_circuit: QuantumCircuit,
    noisy_counts: Dict[str, int],
) -> float:
    """
    Compute fidelity of noisy circuit against ideal state.
    
    Args:
        ideal_circuit: Ideal quantum circuit
        noisy_counts: Measurement counts from noisy circuit
    
    Returns:
        Fidelity value
    """
    # Get ideal statevector
    circuit_no_measure = ideal_circuit.remove_final_measurements(inplace=False)
    ideal_state = Statevector(circuit_no_measure)
    
    # Find target states (states with non-zero amplitude)
    n_qubits = ideal_circuit.num_qubits
    target_states = []
    
    for i, amplitude in enumerate(ideal_state.data):
        if np.abs(amplitude) > 1e-6:
            state_str = format(i, f'0{n_qubits}b')
            target_states.append(state_str)
    
    # Compute empirical fidelity
    return compute_empirical_fidelity(noisy_counts, target_states)


def compute_bell_state_fidelity(counts: Dict[str, int]) -> float:
    """
    Compute fidelity for Bell state measurement.
    
    F = (P(00) + P(11)) / 2
    
    Args:
        counts: Measurement counts
    
    Returns:
        Bell state fidelity
    """
    return compute_empirical_fidelity(counts, ["00", "11"])


def compute_ghz_state_fidelity(counts: Dict[str, int], n_qubits: int) -> float:
    """
    Compute fidelity for GHZ state measurement.
    
    F = (P(00...0) + P(11...1)) / 2
    
    Args:
        counts: Measurement counts
        n_qubits: Number of qubits
    
    Returns:
        GHZ state fidelity
    """
    target_states = ["0" * n_qubits, "1" * n_qubits]
    return compute_empirical_fidelity(counts, target_states)


def compute_average_fidelity(
    fidelity_list: List[float],
    weights: Optional[List[float]] = None,
) -> float:
    """
    Compute weighted average fidelity.
    
    Args:
        fidelity_list: List of fidelity values
        weights: Optional weights (default: equal)
    
    Returns:
        Average fidelity
    """
    if weights is None:
        weights = [1.0] * len(fidelity_list)
    
    total_weight = sum(weights)
    if total_weight == 0:
        return 0.0
    
    return sum(f * w for f, w in zip(fidelity_list, weights)) / total_weight


def fidelity_to_error_rate(fidelity: float, n_qubits: int = 1) -> float:
    """
    Convert fidelity to error rate estimate.
    
    For depolarizing noise: F ≈ 1 - r × (d-1)/d
    where d = 2^n (dimension)
    
    Args:
        fidelity: Measured fidelity
        n_qubits: Number of qubits
    
    Returns:
        Estimated error rate
    """
    d = 2 ** n_qubits
    
    # Solve: F = 1 - r × (d-1)/d
    # r = (1 - F) × d / (d - 1)
    r = (1 - fidelity) * d / (d - 1)
    
    return max(0.0, r)


def print_fidelity_analysis(
    counts: Dict[str, int],
    fidelity: float,
    n_qubits: int = 2,
) -> None:
    """Print detailed fidelity analysis."""
    total = sum(counts.values())
    
    print("Fidelity Analysis")
    print("=" * 40)
    print(f"Total shots: {total}")
    print(f"Overall fidelity: {fidelity:.4f}")
    print(f"\nCounts:")
    
    for state in sorted(counts.keys()):
        prob = counts[state] / total * 100
        print(f"  |{state}⟩: {counts[state]:5d} ({prob:5.1f}%)")
    
    print(f"\nError rate estimate: {fidelity_to_error_rate(fidelity, n_qubits):.6f}")


if __name__ == "__main__":
    # Test fidelity functions
    from qiskit import QuantumCircuit
    
    # Bell state test
    qc = QuantumCircuit(2)
    qc.h(0)
    qc.cx(0, 1)
    
    # Ideal state
    ideal = Statevector(qc.remove_final_measurements(inplace=False))
    print(f"Ideal Bell state: {ideal.data}")
    
    # Compute fidelity between two close states
    f = compute_state_fidelity(ideal, ideal)
    print(f"State fidelity (self): {f:.4f}")
    
    # Empirical fidelity test
    test_counts = {"00": 490, "01": 15, "10": 10, "11": 485}
    emp_f = compute_bell_state_fidelity(test_counts)
    print(f"Empirical Bell fidelity: {emp_f:.4f}")
    
    print_fidelity_analysis(test_counts, emp_f)