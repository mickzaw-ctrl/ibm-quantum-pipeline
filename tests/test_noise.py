"""
Noise Model Tests
=================
"""

import pytest
import sys
sys.path.insert(0, 'src')

from noise_model import (
    create_depolarizing_noise,
    create_thermal_noise,
    get_ibm_backend_noise_model,
)


def test_noise_model_creation():
    """Test depolarizing noise model creation."""
    noise = create_depolarizing_noise(
        one_qubit_error=0.01,
        two_qubit_error=0.02,
        readout_error=0.01,
    )
    
    assert noise is not None
    assert len(noise.basis_gates) > 0


def test_noise_simulation():
    """Test simulation with noise."""
    from pipeline import QuantumPipeline
    
    # Create pipeline with noise
    pipeline = QuantumPipeline(noise_level=0.05)
    
    # Create Bell state
    qc = pipeline.create_bell_state()
    
    # Simulate with noise
    result = pipeline.simulate(qc, shots=1000, use_noise=True)
    
    # Should have reduced fidelity due to noise
    assert result["fidelity"] < 1.0
    assert result["fidelity"] > 0.8  # But not too low


def test_ibm_backend_noise():
    """Test IBM backend noise model."""
    noise = get_ibm_backend_noise_model("ibm_kyiv")
    assert noise is not None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])