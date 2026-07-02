"""
GHZ State Example
=================

Demonstrates creation and simulation of GHZ state.

Run:
    python examples/ghz_state.py
"""

import sys
sys.path.insert(0, 'src')

from pipeline import QuantumPipeline
from fidelity import compute_ghz_state_fidelity


def main():
    print("=" * 60)
    print(" GHZ State Simulation Example")
    print("=" * 60)
    
    # Test different GHZ sizes
    for n_qubits in [2, 3, 4, 5]:
        print(f"\n--- {n_qubits}-qubit GHZ ---")
        
        # Create pipeline
        pipeline = QuantumPipeline(n_qubits=n_qubits, noise_level=0.01)
        
        # Create GHZ state
        circuit = pipeline.create_ghz_state()
        
        print(f"Circuit: {circuit.name}")
        print(f"Qubits: {circuit.num_qubits}")
        print(f"Depth: {circuit.depth()}")
        
        # Simulate
        result = pipeline.simulate(circuit, shots=2000, use_noise=True)
        
        # Compute GHZ fidelity
        f_ghz = compute_ghz_state_fidelity(result['counts'], n_qubits)
        
        print(f"Fidelity: {result['fidelity']:.4f}")
        print(f"GHZ fidelity: {f_ghz:.4f}")
    
    # Compute Quantum Volume
    print("\n--- Quantum Volume ---")
    for n, d in [(5, 5), (10, 10), (50, 50), (127, 100)]:
        qv = 2 ** min(n, d)
        print(f"n={n:3d}, d={d:3d} → QV = {qv}")
    
    print("\n" + "=" * 60)
    print(" Done!")
    print("=" * 60)


if __name__ == "__main__":
    main()