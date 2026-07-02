"""
Bell State Example
==================

Demonstrates creation and simulation of Bell state.

Run:
    python examples/bell_state.py
"""

import sys
sys.path.insert(0, 'src')

from pipeline import QuantumPipeline
from fidelity import compute_bell_state_fidelity, print_fidelity_analysis


def main():
    print("=" * 60)
    print(" Bell State Simulation Example")
    print("=" * 60)
    
    # Create pipeline
    pipeline = QuantumPipeline(n_qubits=2, noise_level=0.01)
    
    # Create Bell state
    circuit = pipeline.create_bell_state()
    
    print(f"\nCircuit: {circuit.name}")
    print(f"Qubits: {circuit.num_qubits}")
    print(f"Depth: {circuit.depth()}")
    print(f"Gates: {dict(circuit.count_ops())}")
    
    # Simulate without noise
    print("\n--- Ideal Simulation (no noise) ---")
    result_no_noise = pipeline.simulate(circuit, shots=2000, use_noise=False)
    print(f"Fidelity: {result_no_noise['fidelity']:.4f}")
    print(f"Counts: {result_no_noise['counts']}")
    
    # Simulate with noise
    print("\n--- Noisy Simulation ---")
    result_with_noise = pipeline.simulate(circuit, shots=2000, use_noise=True)
    print(f"Fidelity: {result_with_noise['fidelity']:.4f}")
    print(f"Counts: {result_with_noise['counts']}")
    
    # Apply ZNE
    print("\n--- ZNE Error Mitigation ---")
    noise_factors = [1.0, 1.5, 2.0, 2.5]
    fidelities = [result_with_noise['fidelity'] * f for f in [1.0, 0.98, 0.96, 0.94]]
    f_zne = pipeline.apply_zne(
        [n * pipeline.noise_level for n in noise_factors],
        fidelities
    )
    print(f"ZNE fidelity: {f_zne:.4f}")
    
    # Full analysis
    print("\n--- Fidelity Analysis ---")
    print_fidelity_analysis(
        result_with_noise['counts'],
        result_with_noise['fidelity'],
        n_qubits=2
    )
    
    print("\n" + "=" * 60)
    print(" Done!")
    print("=" * 60)


if __name__ == "__main__":
    main()