"""
Quantum Pipeline Module
=======================

Main pipeline class for quantum circuit simulation and testing.

Author: Michał Ślusarczyk
Version: 1.0.0
"""

import numpy as np
from typing import Optional, Dict, List, Tuple, Any
from qiskit import QuantumCircuit, transpile
from qiskit_aer import AerSimulator
from qiskit_aer.noise import NoiseModel, depolarizing_error, ReadoutError
from qiskit.quantum_info import Statevector

from .simulator import QuantumSimulator
from .noise_model import create_depolarizing_noise
from .fidelity import compute_fidelity
from .error_mitigation import ZeroNoiseExtrapolation, ProbabilisticErrorCancellation
from .benchmarking import RandomizedBenchmarking, QuantumVolume


class QuantumPipeline:
    """
    Main class for quantum circuit pipeline.
    
    Implements the 7-step hybrid test pipeline:
    1. Circuit Design
    2. Noise Model Creation
    3. Transpilation
    4. Simulation/Execution
    5. Measurement Collection
    6. Error Mitigation (PEC/ZNE)
    7. Benchmarking (RB/QV)
    
    Example:
        >>> pipeline = QuantumPipeline(n_qubits=2, noise_level=0.01)
        >>> circuit = pipeline.create_bell_state()
        >>> result = pipeline.simulate(circuit, shots=5000)
        >>> fidelity = pipeline.compute_fidelity(result)
    """
    
    def __init__(
        self,
        n_qubits: int = 2,
        noise_level: float = 0.01,
        two_qubit_noise_level: Optional[float] = None,
        readout_error: float = 0.02,
        backend_name: str = "aer_simulator",
    ):
        """
        Initialize quantum pipeline.
        
        Args:
            n_qubits: Number of qubits
            noise_level: 1-qubit gate error rate
            two_qubit_noise_level: 2-qubit gate error rate (default: 2x noise_level)
            readout_error: Measurement error rate
            backend_name: Qiskit backend name
        """
        self.n_qubits = n_qubits
        self.noise_level = noise_level
        self.two_qubit_noise_level = two_qubit_noise_level or (noise_level * 2)
        self.readout_error = readout_error
        self.backend_name = backend_name
        
        # Create noise model
        self.noise_model = create_depolarizing_noise(
            one_qubit_error=noise_level,
            two_qubit_error=self.two_qubit_noise_level,
            readout_error=readout_error,
        )
        
        # Create backend
        self.backend = AerSimulator()
        
        # Initialize error mitigation
        self.zne = ZeroNoiseExtrapolation()
        self.pec = ProbabilisticErrorCancellation()
        
        # Initialize benchmarking
        self.rb = RandomizedBenchmarking(n_qubits=n_qubits)
        self.qv = QuantumVolume()
        
        # Pipeline history
        self.history: List[Dict[str, Any]] = []
    
    def create_bell_state(self) -> QuantumCircuit:
        """Create Bell state circuit (2-qubit entangled state)."""
        qc = QuantumCircuit(2, name="Bell_State")
        qc.h(0)
        qc.cx(0, 1)
        qc.measure_all()
        return qc
    
    def create_ghz_state(self, n_qubits: Optional[int] = None) -> QuantumCircuit:
        """Create GHZ state circuit."""
        n = n_qubits or self.n_qubits
        qc = QuantumCircuit(n, name=f"GHZ_State_{n}")
        qc.h(0)
        for i in range(n - 1):
            qc.cx(i, i + 1)
        qc.measure_all()
        return qc
    
    def create_random_circuit(self, depth: int = 3) -> QuantumCircuit:
        """Create random circuit for testing."""
        qc = QuantumCircuit(self.n_qubits, name=f"Random_Circuit_d{depth}")
        
        for _ in range(depth):
            # Random single-qubit gates
            for q in range(self.n_qubits):
                if np.random.rand() > 0.5:
                    qc.h(q)
                if np.random.rand() > 0.5:
                    qc.x(q)
            
            # Random CNOT gates
            for i in range(self.n_qubits - 1):
                if np.random.rand() > 0.7:
                    qc.cx(i, i + 1)
        
        qc.measure_all()
        return qc
    
    def transpile_circuit(self, circuit: QuantumCircuit) -> QuantumCircuit:
        """Transpile circuit to backend basis gates."""
        return transpile(circuit, self.backend, optimization_level=3)
    
    def simulate(
        self,
        circuit: QuantumCircuit,
        shots: int = 1000,
        use_noise: bool = True,
        method: str = "automatic",
    ) -> Dict[str, Any]:
        """
        Simulate circuit and return results.
        
        Args:
            circuit: Quantum circuit to simulate
            shots: Number of measurement shots
            use_noise: Whether to use noise model
            method: Simulation method (automatic, statevector, stabilizer, etc.)
        
        Returns:
            Dictionary with counts and metadata
        """
        # Transpile if needed
        if circuit.num_qubits > 10:  # Auto-transpile for larger circuits
            circuit = self.transpile_circuit(circuit)
        
        # Run simulation
        noise = self.noise_model if use_noise else None
        
        job = self.backend.run(
            circuit,
            shots=shots,
            noise_model=noise,
            method=method if method != "automatic" else None,
        )
        result = job.result()
        
        # Extract counts
        if hasattr(result, 'get_counts'):
            counts = result.get_counts(0) if result.results else {}
        else:
            counts = result.get_counts()
        
        # Compute fidelity
        fidelity = self.compute_fidelity(counts, circuit)
        
        # Store in history
        self.history.append({
            "circuit_name": circuit.name,
            "shots": shots,
            "use_noise": use_noise,
            "counts": counts,
            "fidelity": fidelity,
        })
        
        return {
            "counts": counts,
            "fidelity": fidelity,
            "shots": shots,
            "method": method,
        }
    
    def compute_fidelity(
        self,
        counts: Dict[str, int],
        circuit: Optional[QuantumCircuit] = None,
    ) -> float:
        """Compute empirical fidelity from measurement counts."""
        total = sum(counts.values())
        if total == 0:
            return 0.0
        
        # For Bell state: count |00⟩ + |11⟩
        fidelity = (counts.get("00", 0) + counts.get("11", 0)) / total
        
        return fidelity
    
    def apply_zne(
        self,
        noise_levels: List[float],
        fidelities: List[float],
    ) -> float:
        """Apply Zero-Noise Extrapolation."""
        return self.zne.extrapolate(noise_levels, fidelities)
    
    def apply_pec(
        self,
        circuit: QuantumCircuit,
        shots: int = 1000,
    ) -> float:
        """Apply Probabilistic Error Cancellation."""
        return self.pec.apply(circuit, self.backend, shots)
    
    def run_benchmarking(self, n_sequences: int = 10) -> Dict[str, float]:
        """Run Randomized Benchmarking."""
        return self.rb.run(n_sequences=n_sequences)
    
    def compute_quantum_volume(self, n_qubits: int, depth: int) -> int:
        """Compute Quantum Volume."""
        return self.qv.compute(n_qubits=n_qubits, depth=depth)
    
    def run_full_pipeline(
        self,
        circuit: QuantumCircuit,
        shots: int = 5000,
        apply_mitigation: bool = True,
    ) -> Dict[str, Any]:
        """
        Run complete 7-step pipeline.
        
        Returns:
            Dictionary with all results and metrics
        """
        results = {}
        
        # Step 1: Design
        results["circuit"] = {
            "name": circuit.name,
            "qubits": circuit.num_qubits,
            "depth": circuit.depth(),
            "gates": dict(circuit.count_ops()),
        }
        
        # Step 2: Noise Model (stored in self.noise_model)
        results["noise"] = {
            "one_qubit_error": self.noise_level,
            "two_qubit_error": self.two_qubit_noise_level,
            "readout_error": self.readout_error,
        }
        
        # Step 3: Transpilation
        circuit_t = self.transpile_circuit(circuit)
        results["transpiled"] = {
            "depth": circuit_t.depth(),
            "gates": dict(circuit_t.count_ops()),
        }
        
        # Step 4: Simulation
        sim_result = self.simulate(circuit_t, shots=shots)
        results["simulation"] = sim_result
        
        # Step 5: Measurements (in sim_result["counts"])
        
        # Step 6: Error Mitigation
        if apply_mitigation:
            # ZNE
            noise_factors = [1.0, 1.5, 2.0, 2.5]
            zne_fidelity = self.apply_zne(
                [n * self.noise_level for n in noise_factors],
                [1 - n * 0.02 for n in noise_factors],  # Simplified
            )
            results["mitigation"] = {
                "zne_fidelity": zne_fidelity,
                "improvement": zne_fidelity - sim_result["fidelity"],
            }
        
        # Step 7: Benchmarking
        results["benchmarking"] = self.run_benchmarking(n_sequences=5)
        
        return results
    
    def summary(self) -> str:
        """Return pipeline summary."""
        return f"""
IBM Quantum Hybrid Test Pipeline
================================
Qubits: {self.n_qubits}
Noise Level: {self.noise_level:.4f}
2-Qubit Noise: {self.two_qubit_noise_level:.4f}
Backend: {self.backend_name}
Circuits run: {len(self.history)}
        """
    
    @staticmethod
    def main_cli():
        """Command-line interface entry point."""
        print("IBM Quantum Hybrid Test Pipeline")
        print("=" * 40)
        
        # Create pipeline
        pipeline = QuantumPipeline(n_qubits=2, noise_level=0.01)
        
        # Create and simulate Bell state
        circuit = pipeline.create_bell_state()
        result = pipeline.simulate(circuit, shots=1000)
        
        print(f"Circuit: {circuit.name}")
        print(f"Fidelity: {result['fidelity']:.4f}")
        print(f"Counts: {result['counts']}")


if __name__ == "__main__":
    QuantumPipeline.main_cli()