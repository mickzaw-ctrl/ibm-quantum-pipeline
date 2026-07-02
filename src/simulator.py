"""
Quantum Simulator Module
========================

Wrapper for Qiskit Aer simulator with multiple methods.

Author: Michał Ślusarczyk
Version: 1.0.0
"""

from typing import Optional, Dict, Any, List
import numpy as np
from qiskit import QuantumCircuit
from qiskit_aer import AerSimulator
from qiskit_aer.noise import NoiseModel
from qiskit.quantum_info import Statevector, DensityMatrix


class QuantumSimulator:
    """
    Wrapper for Qiskit Aer quantum simulator.
    
    Supports multiple simulation methods:
    - statevector: Full state vector (no noise)
    - density_matrix: Density matrix (with noise)
    - stabilizer: Clifford circuits (fast)
    - matrix_product_state: MPS for large circuits
    - extended_stabilizer: Extended Clifford
    
    Example:
        >>> sim = QuantumSimulator(noise_model=my_noise)
        >>> result = sim.run(circuit, shots=1000, method='stabilizer')
    """
    
    SUPPORTED_METHODS = [
        "automatic",
        "statevector",
        "density_matrix",
        "stabilizer",
        "extended_stabilizer",
        "matrix_product_state",
    ]
    
    def __init__(self, noise_model: Optional[NoiseModel] = None):
        """
        Initialize simulator.
        
        Args:
            noise_model: Optional noise model to apply
        """
        self.noise_model = noise_model
        self.backend = AerSimulator()
        self.job_history: List[Dict[str, Any]] = []
    
    def run(
        self,
        circuit: QuantumCircuit,
        shots: int = 1000,
        method: str = "automatic",
        memory: bool = False,
    ) -> Dict[str, Any]:
        """
        Run simulation.
        
        Args:
            circuit: Quantum circuit to simulate
            shots: Number of measurement shots
            method: Simulation method
            memory: Whether to return memory
        
        Returns:
            Dictionary with results
        """
        if method not in self.SUPPORTED_METHODS:
            raise ValueError(f"Method must be one of {self.SUPPORTED_METHODS}")
        
        # Configure run options
        run_options = {
            "shots": shots,
            "memory": memory,
        }
        
        if method != "automatic":
            run_options["method"] = method
        
        # Run job
        job = self.backend.run(
            circuit,
            noise_model=self.noise_model,
            **run_options
        )
        result = job.result()
        
        # Extract data
        try:
            counts = result.get_counts(0)
        except Exception:
            counts = {}
        
        # Get statevector if available
        statevector = None
        try:
            if hasattr(result, 'data'):
                sv_data = result.data(0)
                if 'statevector' in sv_data:
                    statevector = sv_data['statevector']
        except Exception:
            pass
        
        # Store in history
        self.job_history.append({
            "circuit_name": circuit.name,
            "shots": shots,
            "method": method,
            "counts": counts,
            "statevector_shape": statevector.shape if statevector is not None else None,
        })
        
        return {
            "counts": counts,
            "statevector": statevector,
            "shots": shots,
            "method": method,
            "job_id": job.job_id() if hasattr(job, 'job_id') else None,
        }
    
    def run_statevector(
        self,
        circuit: QuantumCircuit,
    ) -> Statevector:
        """
        Run statevector simulation (no measurements).
        
        Args:
            circuit: Quantum circuit
        
        Returns:
            Statevector object
        """
        # Remove measurements for statevector simulation
        circuit_no_measure = circuit.remove_final_measurements(inplace=False)
        
        job = self.backend.run(circuit_no_measure, method='statevector', shots=1)
        result = job.result()
        
        try:
            sv_data = result.data(0)
            return sv_data['statevector']
        except Exception:
            return Statevector(circuit_no_measure)
    
    def run_stabilizer(
        self,
        circuit: QuantumCircuit,
        shots: int = 1000,
    ) -> Dict[str, int]:
        """
        Run stabilizer simulation (Clifford circuits only).
        
        Args:
            circuit: Clifford circuit
            shots: Number of shots
        
        Returns:
            Measurement counts
        """
        result = self.run(circuit, shots=shots, method='stabilizer')
        return result["counts"]
    
    def get_bloch_vector(
        self,
        circuit: QuantumCircuit,
    ) -> np.ndarray:
        """
        Calculate Bloch vector for single qubit.
        
        Args:
            circuit: Quantum circuit (must have single qubit with measurements)
        
        Returns:
            Bloch vector [x, y, z]
        """
        sv = self.run_statevector(circuit)
        
        # Calculate Bloch vector components
        rho = DensityMatrix(sv)
        
        # Pauli matrices
        sigma_x = np.array([[0, 1], [1, 0]])
        sigma_y = np.array([[0, -1j], [1j, 0]])
        sigma_z = np.array([[1, 0], [0, -1]])
        
        x = np.real(np.trace(rho @ sigma_x))
        y = np.real(np.trace(rho @ sigma_y))
        z = np.real(np.trace(rho @ sigma_z))
        
        return np.array([x, y, z])
    
    def get_fidelity(
        self,
        counts: Dict[str, int],
        target_state: str = "00",
    ) -> float:
        """
        Calculate empirical fidelity.
        
        Args:
            counts: Measurement counts
            target_state: Target state for fidelity calculation
        
        Returns:
            Empirical fidelity
        """
        total = sum(counts.values())
        if total == 0:
            return 0.0
        
        return counts.get(target_state, 0) / total
    
    def summary(self) -> str:
        """Return simulator summary."""
        return f"""
Quantum Simulator
=================
Backend: {self.backend.name()}
Noise Model: {"Yes" if self.noise_model else "No"}
Jobs run: {len(self.job_history)}
Supported methods: {', '.join(self.SUPPORTED_METHODS)}
        """


if __name__ == "__main__":
    # Test simulator
    from qiskit import QuantumCircuit
    
    sim = QuantumSimulator()
    
    # Bell state
    qc = QuantumCircuit(2)
    qc.h(0)
    qc.cx(0, 1)
    qc.measure_all()
    
    result = sim.run(qc, shots=100)
    print(f"Fidelity: {sim.get_fidelity(result['counts'], '00'):.4f}")
    print(f"Counts: {result['counts']}")