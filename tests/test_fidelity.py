"""
Fidelity Tests
==============
"""

import pytest
import numpy as np
import sys
sys.path.insert(0, 'src')

from fidelity import (
    compute_state_fidelity,
    compute_empirical_fidelity,
    compute_bell_state_fidelity,
    fidelity_to_error_rate,
)


def test_state_fidelity():
    """Test state fidelity computation."""
    # Identical states
    state = np.array([1/np.sqrt(2), 0, 0, 1/np.sqrt(2)], dtype=complex)
    
    f = compute_state_fidelity(state, state)
    assert f > 0.999


def test_bell_fidelity():
    """Test Bell state fidelity."""
    counts = {"00": 490, "11": 490, "01": 10, "10": 10}
    
    f = compute_bell_state_fidelity(counts)
    
    expected = (490 + 490) / 1000
    assert abs(f - expected) < 0.001


def test_empirical_fidelity():
    """Test empirical fidelity computation."""
    counts = {"00": 450, "11": 450, "01": 50, "10": 50}
    
    f = compute_empirical_fidelity(counts, ["00", "11"])
    
    expected = 900 / 1000
    assert abs(f - expected) < 0.001


def test_error_rate_conversion():
    """Test fidelity to error rate conversion."""
    # For 1 qubit: r = (1-F) * 2
    f = 0.99
    r = fidelity_to_error_rate(f, n_qubits=1)
    
    expected = (1 - f) * 2
    assert abs(r - expected) < 0.01


if __name__ == "__main__":
    pytest.main([__file__, "-v"])