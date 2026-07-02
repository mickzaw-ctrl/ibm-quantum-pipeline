"""
Benchmarking Module
==================

Randomized Benchmarking (RB) and Quantum Volume (QV).

Author: Michał Ślusarczyk
Version: 1.0.0
"""

from typing import List, Dict, Optional, Tuple
import numpy as np
from scipy.optimize import curve_fit


class RandomizedBenchmarking:
    """
    Randomized Benchmarking (RB) for measuring Average Gate Fidelity (AGF).
    
    Measures fidelity as function of sequence length m:
        F(m) = A + B * exp(-m/n * r)
    
    where:
        A = (1 - 1/d) [baseline]
        B = 1/d
        d = 2^n (dimension)
        r = decay rate
        n = number of qubits
    
    AGF = 1 - (1 - r) / d
    
    Example:
        >>> rb = RandomizedBenchmarking(n_qubits=2)
        >>> results = rb.run(n_sequences=20)
        >>> print(f"AGF: {results['AGF']:.4f}")
    """
    
    def __init__(self, n_qubits: int = 2):
        """
        Initialize RB.
        
        Args:
            n_qubits: Number of qubits
        """
        self.n_qubits = n_qubits
        self.dimension = 2 ** n_qubits  # d = 2^n
        self.baseline = 1 / self.dimension  # A = 1/d
        self.history: List[Dict] = []
    
    def _generate_clifford_sequence(
        self,
        n_qubits: int,
        sequence_length: int,
        seed: Optional[int] = None,
    ) -> List[str]:
        """
        Generate random Clifford sequence (simplified).
        
        Args:
            n_qubits: Number of qubits
            sequence_length: Number of gates
            seed: Random seed
        
        Returns:
            List of gate names
        """
        rng = np.random.RandomState(seed)
        
        # Single-qubit Clifford gates
        single_qubit_gates = ['h', 's', 'x', 'y', 'z', 'sx', 'sy']
        
        # Generate sequence
        sequence = []
        for _ in range(sequence_length):
            gate = rng.choice(single_qubit_gates)
            qubit = rng.randint(0, n_qubits)
            sequence.append((gate, qubit))
        
        return sequence
    
    def _compute_sequence_fidelity(
        self,
        sequence: List[str],
        n_qubits: int,
    ) -> float:
        """
        Compute fidelity of sequence (simplified model).
        
        Uses exponential decay model.
        """
        # Simplified: fidelity = baseline + (1-baseline) * exp(-r*m)
        m = len(sequence)
        r = 0.01  # Decay rate (typical for good QPU)
        
        fidelity = self.baseline + (1 - self.baseline) * np.exp(-r * m)
        
        return fidelity
    
    def run(
        self,
        n_sequences: int = 10,
        max_sequence_length: int = 16,
        seed: Optional[int] = None,
    ) -> Dict[str, float]:
        """
        Run randomized benchmarking.
        
        Args:
            n_sequences: Number of random sequences per length
            max_sequence_length: Maximum sequence length
            seed: Random seed
        
        Returns:
            Dictionary with decay rate and AGF
        """
        rng = np.random.RandomState(seed)
        
        # Sequence lengths (powers of 2)
        sequence_lengths = [1, 2, 4, 8, max_sequence_length]
        
        # Results storage
        fidelity_data = []
        
        for m in sequence_lengths:
            fidelities = []
            
            for _ in range(n_sequences):
                # Generate and run sequence
                sequence = self._generate_clifford_sequence(
                    self.n_qubits, m, seed=rng.randint(0, 10000)
                )
                f = self._compute_sequence_fidelity(sequence, self.n_qubits)
                fidelities.append(f)
            
            fidelity_data.append((m, np.mean(fidelities)))
        
        # Fit exponential decay
        m_values = [d[0] for d in fidelity_data]
        f_values = [d[1] for d in fidelity_data]
        
        def decay_func(m, r):
            return self.baseline + (1 - self.baseline) * np.exp(-r * m)
        
        try:
            popt, _ = curve_fit(
                decay_func,
                m_values,
                f_values,
                p0=[0.1],
                bounds=([0], [1]),
            )
            r_fitted = popt[0]
        except Exception:
            r_fitted = 0.01  # Default
        
        # Compute AGF
        # For Clifford group: AGF = 1 - (1 - r)^n / d
        # Simplified: AGF ≈ 1 - (1 - r) / d
        agf = 1 - (1 - r_fitted) / self.dimension
        
        # Store in history
        result = {
            "n_qubits": self.n_qubits,
            "n_sequences": n_sequences,
            "max_length": max_sequence_length,
            "decay_rate": r_fitted,
            "AGF": agf,
            "sequence_lengths": m_values,
            "fidelities": f_values,
        }
        self.history.append(result)
        
        return result
    
    def summary(self) -> str:
        """Return RB summary."""
        if not self.history:
            return "Randomized Benchmarking - No data yet"
        
        latest = self.history[-1]
        return f"""
Randomized Benchmarking
=======================
Qubits: {latest['n_qubits']}
Dimension d: {self.dimension}
Decay rate r: {latest['decay_rate']:.6f}
AGF: {latest['AGF']:.6f}
Sequences: {latest['n_sequences']}
        """


class QuantumVolume:
    """
    Quantum Volume (QV) benchmarking.
    
    QV = 2^(min(n, d))
    
    where:
        n = number of qubits
        d = heavy path depth
    
    The heavy path consists of gates with output
    probability > median of all outputs.
    
    Example:
        >>> qv = QuantumVolume()
        >>> result = qv.compute(n_qubits=5, depth=5)
        >>> print(f"QV = {result['QV']}")
    """
    
    def __init__(self):
        """Initialize QV benchmark."""
        self.history: List[Dict] = []
    
    def compute(
        self,
        n_qubits: int,
        depth: int,
    ) -> Dict[str, int]:
        """
        Compute Quantum Volume.
        
        Args:
            n_qubits: Number of qubits
            depth: Circuit depth
        
        Returns:
            Dictionary with QV and parameters
        """
        qv = 2 ** min(n_qubits, depth)
        
        result = {
            "n_qubits": n_qubits,
            "depth": depth,
            "QV": qv,
        }
        
        self.history.append(result)
        
        return result
    
    def estimate_qv_from_rb(
        self,
        agf: float,
        n_qubits: int,
    ) -> int:
        """
        Estimate QV from AGF.
        
        Lower bound on QV from gate fidelity.
        
        Args:
            agf: Average Gate Fidelity
            n_qubits: Number of qubits
        
        Returns:
            Estimated QV
        """
        # From QV definition: AGF > 1/2 implies QV >= 2^n
        # More precise: heavy path probability > 2/3
        
        if agf > 0.99:
            # Good enough for full QV
            return 2 ** n_qubits
        elif agf > 0.95:
            # Moderate QV
            return 2 ** max(1, n_qubits - 1)
        elif agf > 0.8:
            # Limited QV
            return 2 ** max(1, n_qubits - 2)
        else:
            # Low QV
            return 2
        
    def summary(self) -> str:
        """Return QV summary."""
        if not self.history:
            return "Quantum Volume - No data yet"
        
        latest = self.history[-1]
        return f"""
Quantum Volume
==============
Qubits: {latest['n_qubits']}
Depth: {latest['depth']}
QV: {latest['QV']}
        """


class TomographyBenchmark:
    """
    Quantum State/Process Tomography benchmarking.
    """
    
    def __init__(self, n_qubits: int = 2):
        self.n_qubits = n_qubits
        self.measurements: List[Dict] = []
    
    def run_state_tomography(
        self,
        counts: Dict[str, int],
    ) -> np.ndarray:
        """
        Reconstruct density matrix from measurements.
        
        Simplified maximum likelihood estimation.
        
        Args:
            counts: Measurement counts
        
        Returns:
            Reconstructed density matrix
        """
        n = self.n_qubits
        d = 2 ** n  # Dimension
        
        # Initialize
        rho = np.zeros((d, d), dtype=complex)
        
        # Populate from counts
        total = sum(counts.values())
        
        for state, count in counts.items():
            # Convert state string to basis index
            idx = int(state, 2) if state else 0
            
            # Add contribution
            basis_vec = np.zeros(d)
            basis_vec[idx] = 1.0
            
            rho += (count / total) * np.outer(basis_vec, basis_vec.conj())
        
        # Trace normalize
        rho = rho / np.trace(rho)
        
        return rho
    
    def compute_purity(self, rho: np.ndarray) -> float:
        """Compute purity Tr(ρ²)."""
        return float(np.real(np.trace(rho @ rho)))
    
    def compute_fidelity_with_theory(
        self,
        rho: np.ndarray,
        psi_theory: np.ndarray,
    ) -> float:
        """Compute fidelity with theoretical state."""
        # F = ⟨ψ|ρ|ψ⟩
        return float(np.abs(np.vdot(psi_theory, rho @ psi_theory)))


if __name__ == "__main__":
    # Test RB
    print("Testing Randomized Benchmarking...")
    
    rb = RandomizedBenchmarking(n_qubits=2)
    results = rb.run(n_sequences=10)
    
    print(f"Decay rate: {results['decay_rate']:.6f}")
    print(f"AGF: {results['AGF']:.6f}")
    
    # Test QV
    print("\nTesting Quantum Volume...")
    
    qv = QuantumVolume()
    
    test_cases = [
        (5, 5),
        (7, 4),
        (127, 100),
    ]
    
    for n, d in test_cases:
        result = qv.compute(n, d)
        print(f"  n={n}, d={d} → QV={result['QV']}")
    
    print("\n" + rb.summary())
    print(qv.summary())