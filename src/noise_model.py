"""
Noise Model Module
==================

Factory functions for creating quantum noise models.

Author: Michał Ślusarczyk
Version: 1.0.0
"""

from typing import Optional, List, Tuple
from qiskit_aer.noise import NoiseModel, depolarizing_error, thermal_error
from qiskit_aer.noise.errors import ReadoutError


def create_depolarizing_noise(
    one_qubit_error: float = 0.001,
    two_qubit_error: float = 0.01,
    readout_error: float = 0.01,
    basis_gates: Optional[List[str]] = None,
) -> NoiseModel:
    """
    Create depolarizing noise model.
    
    The depolarizing channel:
        ρ' = (1 - p)ρ + p/3 (XρX + YρY + ZρZ)
    
    Args:
        one_qubit_error: Single-qubit gate error probability
        two_qubit_error: Two-qubit gate error probability
        readout_error: Measurement error probability
        basis_gates: List of basis gates to apply errors to
    
    Returns:
        Configured NoiseModel
    
    Example:
        >>> noise = create_depolarizing_noise(0.001, 0.01, 0.02)
        >>> noise.basis_gates
        ['cx', 'h', 'id', 'reset', 'rz', 'sx', 'x']
    """
    noise_model = NoiseModel()
    
    # Default basis gates
    if basis_gates is None:
        basis_gates = [
            'x', 'y', 'z', 'h', 's', 'sx', 'rx', 'ry', 'rz',
            'cx', 'cz', 'swap', 'iswap', 'cphase'
        ]
    
    # Single-qubit error
    error_1q = depolarizing_error(one_qubit_error, 1)
    
    # Two-qubit error
    error_2q = depolarizing_error(two_qubit_error, 2)
    
    # Add errors to gates
    single_qubit_gates = ['x', 'y', 'z', 'h', 's', 'sx', 'rx', 'ry', 'rz', 'u1', 'u2', 'u3']
    two_qubit_gates = ['cx', 'cz', 'swap', 'iswap', 'cphase', 'cp']
    
    for gate in single_qubit_gates:
        if gate in basis_gates:
            noise_model.add_all_qubit_quantum_error(error_1q, [gate])
    
    for gate in two_qubit_gates:
        if gate in basis_gates:
            noise_model.add_all_qubit_quantum_error(error_2q, [gate])
    
    # Readout error
    if readout_error > 0:
        # Create symmetric readout error
        p0_given_0 = 1 - readout_error
        p1_given_1 = 1 - readout_error
        readout_err = ReadoutError([[p0_given_0, readout_error], [readout_error, p1_given_1]])
        noise_model.add_all_qubit_readout_error(readout_err)
    
    return noise_model


def create_thermal_noise(
    t1: float = 100e-6,  # Relaxation time in seconds
    t2: float = 100e-6,  # Dephasing time in seconds
    thermal_population: float = 0.0,
    frequency: float = 5e9,
) -> NoiseModel:
    """
    Create thermal noise model based on T1/T2 times.
    
    Args:
        t1: Relaxation time (μs)
        t2: Dephasing time (μs)
        thermal_population: Thermal population of excited state
        frequency: Qubit frequency (Hz)
    
    Returns:
        NoiseModel with thermal errors
    """
    noise_model = NoiseModel()
    
    # Thermal relaxation error
    thermal_relaxation_error = thermal_error(
        t1=t1,
        t2=t2,
        thermal_population=thermal_population,
        dt=1e-9,  # 1ns time resolution
    )
    
    # Add to all gates (simplified)
    noise_model.add_all_qubit_quantum_error(thermal_relaxation_error, ["x", "sx"])
    
    return noise_model


def create_readout_error(
    assignment_error_matrix: List[List[float]],
) -> NoiseModel:
    """
    Create custom readout error model.
    
    Args:
        assignment_error_matrix: 2x2 matrix of P(measured|actual)
    
    Returns:
        NoiseModel with custom readout errors
    """
    noise_model = NoiseModel()
    
    readout_error = ReadoutError(assignment_error_matrix)
    noise_model.add_all_qubit_readout_error(readout_error)
    
    return noise_model


def create_correlated_noise(
    one_qubit_error: float = 0.001,
    correlation_strength: float = 0.5,
) -> NoiseModel:
    """
    Create correlated noise model (simplified).
    
    Args:
        one_qubit_error: Base single-qubit error
        correlation_strength: Strength of correlation (0-1)
    
    Returns:
        NoiseModel with correlated errors
    """
    noise_model = NoiseModel()
    
    # Standard depolarizing error
    error_1q = depolarizing_error(one_qubit_error, 1)
    error_2q = depolarizing_error(one_qubit_error * (1 + correlation_strength), 2)
    
    noise_model.add_all_qubit_quantum_error(error_1q, ['h', 'x', 'y', 'z'])
    noise_model.add_all_qubit_quantum_error(error_2q, ['cx'])
    
    return noise_model


def get_ibm_backend_noise_model(
    backend_name: str = "ibm_kyiv",
    gate_error_scale: float = 1.0,
) -> NoiseModel:
    """
    Get noise model approximating real IBM backend.
    
    Args:
        backend_name: IBM backend name
        gate_error_scale: Scale factor for gate errors
    
    Returns:
        Approximate noise model for specified backend
    """
    # Approximate values for different backends
    backend_specs = {
        "ibm_kyiv": {
            "1q_error": 0.0003,
            "2q_error": 0.0008,
            "readout_error": 0.02,
        },
        "ibm_brisbane": {
            "1q_error": 0.0002,
            "2q_error": 0.0005,
            "readout_error": 0.015,
        },
        "ibm_washington": {
            "1q_error": 0.0004,
            "2q_error": 0.001,
            "readout_error": 0.03,
        },
    }
    
    specs = backend_specs.get(backend_name, backend_specs["ibm_kyiv"])
    
    return create_depolarizing_noise(
        one_qubit_error=specs["1q_error"] * gate_error_scale,
        two_qubit_error=specs["2q_error"] * gate_error_scale,
        readout_error=specs["readout_error"] * gate_error_scale,
    )


def print_noise_model_info(noise_model: NoiseModel) -> None:
    """Print information about a noise model."""
    print(f"Noise Model Information")
    print(f"=" * 40)
    print(f"Basis gates: {noise_model.basis_gates}")
    print(f"Number of error types: {len(noise_model.error_methods)}")
    
    if noise_model.local_quantum_errors:
        print(f"\nLocal quantum errors: {len(noise_model.local_quantum_errors)}")
    
    if noise_model.local_readout_errors:
        print(f"Local readout errors: {len(noise_model.local_readout_errors)}")
    
    if noise_model.all_qubit_readout_errors:
        print(f"All-qubit readout errors: {len(noise_model.all_qubit_readout_errors)}")


if __name__ == "__main__":
    # Test noise models
    print("Testing noise models...")
    
    # Depolarizing
    noise1 = create_depolarizing_noise(0.01, 0.02, 0.01)
    print_noise_model_info(noise1)
    
    # IBM backend approximation
    noise2 = get_ibm_backend_noise_model("ibm_kyiv")
    print("\nIBM Kyiv approximation:")
    print_noise_model_info(noise2)