"""
IBM Quantum Hybrid Test Pipeline
---------------------------------

A complete quantum computing test pipeline with Qiskit Aer,
noise modeling, error mitigation, and benchmarking.

Example usage:
    from src.pipeline import QuantumPipeline
    
    pipeline = QuantumPipeline(n_qubits=2)
    circuit = pipeline.create_bell_state()
    result = pipeline.simulate(circuit, shots=1000)
"""

__version__ = "1.0.0"
__author__ = "Michał Ślusarczyk"

from .pipeline import QuantumPipeline
from .simulator import QuantumSimulator
from .noise_model import create_depolarizing_noise
from .fidelity import compute_fidelity
from .error_mitigation import ZeroNoiseExtrapolation, ProbabilisticErrorCancellation

__all__ = [
    "QuantumPipeline",
    "QuantumSimulator",
    "create_depolarizing_noise",
    "compute_fidelity",
    "ZeroNoiseExtrapolation",
    "ProbabilisticErrorCancellation",
]