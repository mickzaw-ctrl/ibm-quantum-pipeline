"""
Circuit Tests
=============
"""

import pytest
import numpy as np
from qiskit import QuantumCircuit
from qiskit.quantum_info import Statevector

# Import from src
import sys
sys.path.insert(0, 'src')

from pipeline import QuantumPipeline
from simulator import QuantumSimulator


def test_bell_state():
    """Test Bell state circuit creation and simulation."""
    # Create pipeline
    pipeline = QuantumPipeline(n_qubits=2)
    
    # Create Bell state
    qc = pipeline.create_bell_state()
    
    # Verify structure
    assert qc.num_qubits == 2
    assert qc.name == "Bell_State"
    
    # Get ideal statevector
    qc_no_measure = qc.remove_final_measurements(inplace=False)
    state = Statevector(qc_no_measure)
    
    # Expected: (|00⟩ + |11⟩)/√2
    expected_state = np.array([1/np.sqrt(2), 0, 0, 1/np.sqrt(2)])
    
    # Check fidelity
    fidelity = np.abs(np.vdot(expected_state, state.data))**2
    
    assert fidelity > 0.999, f"Bell state fidelity should be ~1.0, got {fidelity}"
    
    # Simulate
    result = pipeline.simulate(qc, shots=1000, use_noise=False)
    
    assert "counts" in result
    assert "fidelity" in result
    assert result["fidelity"] > 0.99  # Should be nearly perfect without noise


def test_ghz_state():
    """Test GHZ state creation."""
    pipeline = QuantumPipeline(n_qubits=3)
    
    # Create GHZ state
    qc = pipeline.create_ghz_state()
    
    assert qc.num_qubits == 3
    assert "GHZ" in qc.name
    
    # Verify statevector
    qc_no_measure = qc.remove_final_measurements(inplace=False)
    state = Statevector(qc_no_measure)
    
    # Expected: (|000⟩ + |111⟩)/√2
    assert np.abs(state.data[0]) > 0.7  # |000⟩ amplitude
    assert np.abs(state.data[7]) > 0.7  # |111⟩ amplitude


def test_random_circuit():
    """Test random circuit generation."""
    pipeline = QuantumPipeline(n_qubits=3)
    
    # Create random circuit
    qc = pipeline.create_random_circuit(depth=5)
    
    assert qc.num_qubits == 3
    assert qc.depth() > 0
    
    # Simulate
    result = pipeline.simulate(qc, shots=100)
    assert "counts" in result


def test_transpilation():
    """Test circuit transpilation."""
    pipeline = QuantumPipeline()
    
    # Create circuit with T gate
    qc = QuantumCircuit(2)
    qc.h(0)
    qc.t(0)  # Not in IBM basis
    qc.cx(0, 1)
    qc.measure_all()
    
    # Transpile
    qc_t = pipeline.transpile_circuit(qc)
    
    # Should succeed
    assert qc_t.num_qubits == 2
    assert qc_t.depth() >= qc.depth()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])