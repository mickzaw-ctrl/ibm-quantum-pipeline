"""
Pipeline Integration Tests
==========================
"""

import pytest
import sys
sys.path.insert(0, 'src')

from pipeline import QuantumPipeline


def test_full_pipeline():
    """Test complete pipeline execution."""
    # Create pipeline
    pipeline = QuantumPipeline(n_qubits=2, noise_level=0.01)
    
    # Create circuit
    circuit = pipeline.create_bell_state()
    
    # Run full pipeline
    results = pipeline.run_full_pipeline(circuit, shots=500)
    
    # Check all steps completed
    assert "circuit" in results
    assert "noise" in results
    assert "transpiled" in results
    assert "simulation" in results
    assert "benchmarking" in results
    
    # Check circuit info
    assert results["circuit"]["qubits"] == 2
    assert results["circuit"]["name"] == "Bell_State"
    
    # Check simulation results
    assert "fidelity" in results["simulation"]
    assert 0 < results["simulation"]["fidelity"] <= 1.0
    
    # Check noise info
    assert results["noise"]["one_qubit_error"] == 0.01


def test_zne():
    """Test ZNE error mitigation."""
    pipeline = QuantumPipeline()
    
    noise_levels = [0.01, 0.015, 0.02]
    fidelities = [0.98, 0.97, 0.96]
    
    f_zne = pipeline.apply_zne(noise_levels, fidelities)
    
    # ZNE should extrapolate to higher fidelity
    assert f_zne > max(fidelities)


def test_benchmarking():
    """Test RB benchmarking."""
    pipeline = QuantumPipeline()
    
    results = pipeline.run_benchmarking(n_sequences=5)
    
    assert "AGF" in results
    assert "decay_rate" in results
    assert 0 < results["AGF"] <= 1.0


def test_quantum_volume():
    """Test QV computation."""
    pipeline = QuantumPipeline()
    
    qv = pipeline.compute_quantum_volume(n_qubits=5, depth=5)
    
    assert qv == 32  # 2^min(5,5)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])