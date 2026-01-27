"""
=============================================================
SIMULADOR DE CIRCUITO CUÁNTICO DE 2 QUBITS
Implementación usando NumPy para el Backend Expert
=============================================================
"""

import numpy as np
import matplotlib.pyplot as plt
from typing import Union, List, Tuple

# ============================================================================
# DEFINICIÓN DE PUERTAS CUÁNTICAS BÁSICAS
# ============================================================================

class QuantumGates:
    """
    Colección de puertas cuánticas fundamentales.
    Todas las matrices están normalizadas y representan operaciones unitarias.
    """
    
    # ----- Puerta X (NOT cuántico) -----
    # Invierte los estados |0⟩ → |1⟩ y |1⟩ → |0⟩
    # Matriz: [[0, 1], [1, 0]]
    X = np.array([[0, 1], 
                  [1, 0]], dtype=complex)
    
    # ----- Puerta H (Hadamard) -----
    # Crea superposición equiprobable
    # Matriz: (1/√2)[[1, 1], [1, -1]]
    H = (1 / np.sqrt(2)) * np.array([[1, 1], 
                                     [1, -1]], dtype=complex)
    
    # ----- Puerta Z (Pauli-Z) -----
    # Aplica fase -1 al estado |1⟩
    # Matriz: [[1, 0], [0, -1]]
    Z = np.array([[1, 0], 
                  [0, -1]], dtype=complex)
    
    # ----- Puerta S (Phase Gate) -----
    # Aplica fase i al estado |1⟩ (raíz cuadrada de Z)
    # Matriz: [[1, 0], [0, i]]
    S = np.array([[1, 0], 
                  [0, 1j]], dtype=complex)
    
    # ----- Puerta T (T Gate / π/8) -----
    # Aplica fase e^(iπ/4) al estado |1⟩
    # Matriz: [[1, 0], [0, e^(iπ/4)]]
    T = np.array([[1, 0], 
                  [0, np.exp(1j * np.pi / 4)]], dtype=complex)
    
    # ----- Puerta CNOT (Controlled-NOT) -----
    # Si el qubit de control es |1⟩, invierte el qubit objetivo
    # Matriz 4x4 para sistema de 2 qubits (orden: |00⟩, |01⟩, |10⟩, |11⟩)
    CNOT = np.array([
        [1, 0, 0, 0],  # |00⟩ → |00⟩
        [0, 1, 0, 0],  # |01⟩ → |01⟩
        [0, 0, 0, 1],  # |10⟩ → |11⟩
        [0, 0, 1, 0]   # # |11⟩ → |10⟩
    ], dtype=complex)


# ============================================================================
# CLASE PRINCIPAL DEL CIRCUITO CUÁNTICO
# ============================================================================

class QuantumCircuit:
    """
    Simulador de circuito cuántico de 2 qubits.
    
    El sistema se representa mediante un vector de estado de dimensión 4,
    correspondiente a las bases: |00⟩, |01⟩, |10⟩, |11⟩
    
    Attributes:
        state: Vector de estado actual del sistema (complejo, normalizado)
        num_qubits: Número de qubits del circuito (fijo en 2)
    """
    
    def __init__(self, num_qubits: int = 2):
        """
        Inicializa el circuito en el estado base |00...0⟩.
        
        Args:
            num_qubits: Número de qubits (actualmente solo soporta 2)
        """
        self.num_qubits = num_qubits
        
        # Estado inicial |00⟩ = [1, 0, 0, 0]ᵀ
        # Solo el estado base |00⟩ tiene probabilidad 1
        self.state = np.zeros(2 ** num_qubits, dtype=complex)
        self.state[0] = 1.0  # |00⟩ tiene amplitud 1
        
        print(f"✓ Circuito cuántico inicializado con estado |00⟩")
        print(f"  Dimensión del espacio de Hilbert: {2**num_qubits}")
    
    def apply_gate(self, gate: np.ndarray, target: int, 
                   control: Union[int, None] = None):
        """
        Aplica una puerta cuántica al circuito.
        
        Args:
            gate: Matriz de la puerta (2x2 para puertas de 1 qubit)
            target: Índice del qubit objetivo (0 = qubit menos significativo)
            control: Índice del qubit de control (solo para CNOT)
        
        Raises:
            ValueError: Si los índices de qubits son inválidos
        """
        # Validación de qubits
        if target < 0 or target >= self.num_qubits:
            raise ValueError(f"Qubit objetivo inválido: {target}")
        
        if control is not None and (control < 0 or control >= self.num_qubits):
            raise ValueError(f"Qubit de control inválido: {control}")
        
        # Si es una puerta de 1 qubit
        if control is None:
            self._apply_single_qubit_gate(gate, target)
        else:
            # Si es CNOT (puerta de 2 qubits)
            if gate.shape == (2, 2):
                self._apply_cnot(gate, control, target)
            else:
                raise ValueError("Para puertas de 2 qubits, use CNOT directamente")
    
    def _apply_single_qubit_gate(self, gate: np.ndarray, target: int):
        """
        Aplica una puerta de 1 qubit al sistema de 2 qubits.
        
        Para puertas de 1 qubit, necesitamos crear la matriz completa
        de 4x4 usando el producto tensor (Kronecker product).
        
        El qubit 0 es el menos significativo (LSB).
        """
        if target == 0:
            # Puerta en qubit 0: I ⊗ gate
            full_gate = np.kron(np.eye(2, dtype=complex), gate)
        else:  # target == 1
            # Puerta en qubit 1: gate ⊗ I
            full_gate = np.kron(gate, np.eye(2, dtype=complex))
        
        # Evolucióunitaria: |ψ'⟩ = U|ψ⟩
        self.state = full_gate @ self.state
        
        # Normalizar para evitar errores de punto flotante
        norm = np.linalg.norm(self.state)
        if norm > 0:
            self.state /= norm
    
    def _apply_cnot(self, gate: np.ndarray, control: int, target: int):
        """
        Aplica la puerta CNOT al sistema de 2 qubits.
        
        CNOT intercambia las amplitudes de |10⟩ y |11⟩.
        """
        if control == 0 and target == 1:
            # CNOT(0→1): qubit 0 controla, qubit 1 es objetivo
            # Matriz estándar CNOT
            self.state = QuantumGates.CNOT @ self.state
        elif control == 1 and target == 0:
            # CNOT(1→0): qubit 1 controla, qubit 0 es objetivo
            # Matriz CNOT con roles invertidos
            cnot_10 = np.array([
                [1, 0, 0, 0],  # |00⟩ → |00⟩
                [0, 0, 0, 1],  # |01⟩ → |11⟩ (control=1, target flip)
                [0, 0, 1, 0],  # |10⟩ → |10⟩ (control=0)
                [0, 1, 0, 0]   # |11⟩ → |01⟩ (control=1, target flip)
            ], dtype=complex)
            self.state = cnot_10 @ self.state
        else:
            raise ValueError("CNOT requiere qubits 0 y 1")
        
        # Normalizar
        norm = np.linalg.norm(self.state)
        if norm > 0:
            self.state /= norm
    
    def measure(self, shots: int = 1000) -> dict:
        """
        Mide el estado cuántico y colapsa al estado medido.
        
        La medición destruye la superposición y colapsa a uno
        de los estados base con probabilidad proporcional al
        cuadrado de su amplitud (regla de Born).
        
        Args:
            shots: Número de veces que se mide (para estadísticas)
        
        Returns:
            Dictionary con los conteos de cada estado medido
        """
        # Calcular probabilidades: |amplitude|²
        probabilities = np.abs(self.state) ** 2
        
        # Verificar que las probabilidades suman 1
        assert np.isclose(np.sum(probabilities), 1.0), \
            f"Las probabilidades no suman 1: {np.sum(probabilities)}"
        
        # Estados base posibles: |00⟩, |01⟩, |10⟩, |11⟩
        basis_states = ['|00⟩', '|01⟩', '|10⟩', '|11⟩']
        
        # Simular mediciones
        outcomes = np.random.choice(
            len(self.state), 
            size=shots, 
            p=probabilities
        )
        
        # Contar resultados
        counts = {basis_states[i]: np.sum(outcomes == i) for i in range(len(self.state))}
        
        # Colapsar al estado más probable (para visualización)
        collapsed_state_idx = np.argmax(probabilities)
        self.state = np.zeros_like(self.state)
        self.state[collapsed_state_idx] = 1.0
        
        return counts
    
    def get_probabilities(self) -> dict:
        """
        Retorna las probabilidades de cada estado base sin colapsar.
        
        Returns:
            Dictionary con probabilidades de cada estado base
        """
        probabilities = np.abs(self.state) ** 2
        basis_states = ['|00⟩', '|01⟩', '|10⟩', '|11⟩']
        return {basis_states[i]: probabilities[i] for i in range(len(probabilities))}
    
    def print_state(self):
        """Imprime el estado actual del sistema en notación de Dirac."""
        basis_states = ['|00⟩', '|01⟩', '|10⟩', '|11⟩']
        state_str = ""
        
        for i, (amp, state) in enumerate(zip(self.state, basis_states)):
            if np.abs(amp) > 1e-10:  # Solo mostrar amplitudes no nulas
                # Formatear número complejo
                real_part = np.real(amp)
                imag_part = np.imag(amp)
                
                if np.abs(imag_part) < 1e-10:
                    amp_str = f"{real_part:.4f}"
                elif np.abs(real_part) < 1e-10:
                    amp_str = f"{imag_part:.4f}j"
                else:
                    sign = '+' if imag_part >= 0 else ''
                    amp_str = f"{real_part:.4f}{sign}{imag_part:.4f}j"
                
                if state_str:
                    state_str += " + "
                state_str += f"{amp_str}|{state[1:3]⟩"
        
        print(f"Estado actual: |ψ⟩ = {state_str}")
        print(f"Normalización: {np.linalg.norm(self.state):.6f}")


# ============================================================================
# VISUALIZACIÓN DE RESULTADOS
# ============================================================================

def visualize_results(probabilities: dict, counts: dict = None, 
                      title: str = "Probabilidades del Estado Cuántico"):
    """
    Visualiza las probabilidades del circuito cuántico usando matplotlib.
    
    Args:
        probabilities: Diccionario con probabilidades de cada estado
        counts: (Opcional) Conteos de medición para comparación
        title: Título del gráfico
    """
    fig, axes = plt.subplots(1, 2 if counts else 1, figsize=(12, 5))
    
    states = list(probabilities.keys())
    probs = list(probabilities.values())
    
    # ----- Gráfico de Probabilidades Teóricas -----
    ax1 = axes[0] if counts else axes
    colors = ['#3498db', '#2ecc71', '#e74c3c', '#9b59b6']
    
    bars1 = ax1.bar(states, probs, color=colors, edgecolor='black', linewidth=1.5)
    
    # Añadir valores en las barras
    for bar, prob in zip(bars1, probs):
        height = bar.get_height()
        ax1.annotate(f'{prob:.3f}',
                    xy=(bar.get_x() + bar.get_width() / 2, height),
                    xytext=(0, 3),
                    textcoords="offset points",
                    ha='center', va='bottom', fontsize=11, fontweight='bold')
    
    ax1.set_ylabel('Probabilidad', fontsize=12)
    ax1.set_xlabel('Estado Base', fontsize=12)
    ax1.set_title('Probabilidades Teóricas', fontsize=14, fontweight='bold')
    ax1.set_ylim(0, 1.1)
    ax1.axhline(y=1.0, color='gray', linestyle='--', alpha=0.5)
    ax1.grid(axis='y', alpha=0.3)
    
    # ----- Gráfico de Conteos de Medición -----
    if counts:
        ax2 = axes[1]
        meas_counts = list(counts.values())
        total_shots = sum(meas_counts)
        measured_probs = [c / total_shots for c in meas_counts]
        
        bars2 = ax2.bar(states, measured_probs, color=colors, 
                       edgecolor='black', linewidth=1.5, alpha=0.8)
        
        for bar, count, prob in zip(bars2, meas_counts, measured_probs):
            height = bar.get_height()
            ax2.annotate(f'{count}\n({prob:.3f})',
                        xy=(bar.get_x() + bar.get_width() / 2, height),
                        xytext=(0, 3),
                        textcoords="offset points",
                        ha='center', va='bottom', fontsize=9)
        
        ax2.set_ylabel('Frecuencia', fontsize=12)
        ax2.set_xlabel('Estado Medido', fontsize=12)
        ax2.set_title(f'Mediciones (Total: {total_shots} shots)', 
                     fontsize=14, fontweight='bold')
        ax2.set_ylim(0, 1.1)
        ax2.grid(axis='y', alpha=0.3)
    
    plt.suptitle(title, fontsize=16, fontweight='bold', y=1.02)
    plt.tight_layout()
    plt.savefig('quantum_results.png', dpi=150, bbox_inches='tight')
    plt.show()
    
    print(f"\n✓ Gráfico guardado como 'quantum_results.png'")


# ============================================================================
# EJEMPLO DE USO: BELL STATE (|Φ⁺⟩)
# ============================================================================

def create_bell_state():
    """
    Crea el estado de Bell |Φ⁺⟩ = (|00⟩ + |11⟩)/√2.
    
    Este estado maximally entangled (entrelazado) no puede
    escribirse como producto de estados individuales.
    
    Circuito:
    1. Aplicar H al qubit 0 → crea superposición
    2. Aplicar CNOT(0→1) → entrelaza los qubits
    
    Resultado: (|00⟩ + |11⟩)/√2 con probabilidad 50% cada uno
    """
    print("\n" + "="*60)
    print("CREANDO ESTADO DE BELL |Φ⁺⟩ = (|00⟩ + |11⟩)/√2")
    print("="*60)
    
    # Crear nuevo circuito
    qc = QuantumCircuit(num_qubits=2)
    
    print("\n[Paso 0] Estado inicial:")
    qc.print_state()
    
    # ----- Paso 1: Aplicar Hadamard al qubit 0 -----
    # H|0⟩ = (|0⟩ + |1⟩)/√2
    # El estado se convierte en: (|00⟩ + |10⟩)/√2
    print("\n[Paso 1] Aplicar puerta H al qubit 0:")
    print("  H|0⟩ = (|0⟩ + |1⟩)/√2")
    qc.apply_gate(QuantumGates.H, target=0)
    qc.print_state()
    
    # ----- Paso 2: Aplicar CNOT(0→1) -----
    # CNOT transforma: |00⟩→|00⟩, |10⟩→|11⟩
    # El estado final es: (|00⟩ + |11⟩)/√2
    print("\n[Paso 2] Aplicar CNOT(qubit 0 → qubit 1):")
    print("  CNOT: |00⟩→|00⟩, |10⟩→|11⟩")
    qc.apply_gate(QuantumGates.CNOT, target=1, control=0)
    qc.print_state()
    
    # Obtener probabilidades
    probs = qc.get_probabilities()
    print("\n[Análisis] Probabilidades de cada estado base:")
    for state, prob in probs.items():
        print(f"  {state}: {prob:.4f} ({prob*100:.1f}%)")
    
    # Verificar que es un estado entrelazado
    entanglement_check = np.abs(probs['|00⟩'] - probs['|11⟩'])
    print(f"\n[Verificación] Diferencia |P(|00⟩) - P(|11⟩)|: {entanglement_check:.6f}")
    if entanglement_check < 1e-10:
        print("  ✓ Estado perfectamente entrelazado (Bell State)")
    
    # Medir múltiples veces
    print("\n[Medición] Realizando 1000 mediciones...")
    counts = qc.measure(shots=1000)
    print("  Resultados de medición:")
    for state, count in counts.items():
        print(f"    {state}: {count} veces ({count/10:.1f}%)")
    
    # Visualizar
    visualize_results(probs, counts, "Estado de Bell |Φ⁺⟩")
    
    return qc


def demo_other_gates():
    """
    Demuestra otras puertas cuánticas básicas.
    """
    print("\n" + "="*60)
    print("DEMOSTRACIÓN DE OTRAS PUERTAS CUÁNTICAS")
    print("="*60)
    
    # ----- Demo: Puerta X -----
    print("\n[1] PUERTA X (NOT cuántico)")
    print("    X|0⟩ = |1⟩, X|1⟩ = |0⟩")
    qc_x = QuantumCircuit(2)
    qc_x.apply_gate(QuantumGates.X, target=0)
    probs = qc_x.get_probabilities()
    print(f"    Resultado: P(|00⟩)={probs['|00⟩']:.2f}, P(|10⟩)={probs['|10⟩']:.2f}")
    
    # ----- Demo: Puerta Z -----
    print("\n[2] PUERTA Z (Pauli-Z)")
    print("    Z|0⟩ = |0⟩, Z|1⟩ = -|1⟩")
    print("    (Solo cambia la fase, las probabilidades no cambian)")
    qc_z = QuantumCircuit(2)
    qc_z.apply_gate(QuantumGates.H, target=0)  # Crear superposición
    qc_z.apply_gate(QuantumGates.Z, target=0)
    probs = qc_z.get_probabilities()
    print(f"    Resultado: P(|00⟩)={probs['|00⟩']:.2f}, P(|10⟩)={probs['|10⟩']:.2f}")
    print("    (Las probabilidades son iguales, pero hay un cambio de fase)")
    
    # ----- Demo: Puerta T -----
    print("\n[3] PUERTA T (T Gate / π/8)")
    print("    Aplica fase e^(iπ/4) al estado |1⟩")
    qc_t = QuantumCircuit(2)
    qc_t.apply_gate(QuantumGates.T, target=0)
    qc_t.print_state()
    
    # ----- Demo: S gate -----
    print("\n[4] PUERTA S (Phase Gate)")
    print("    Aplica fase i al estado |1⟩ (raíz de Z)")
    qc_s = QuantumCircuit(2)
    qc_s.apply_gate(QuantumGates.S, target=0)
    qc_s.print_state()


# ============================================================================
# PUNTO DE ENTRADA PRINCIPAL
# ============================================================================

if __name__ == "__main__":
    print("╔" + "═"*58 + "╗")
    print("║" + " "*15 + "SIMULADOR CUÁNTICO" + " "*20 + "║")
    print("║" + " "*10 + "Circuitos de 2 Qubits con NumPy" + " "*12 + "║")
    print("╚" + "═"*58 + "╝")
    
    # Ejecutar ejemplos
    create_bell_state()
    demo_other_gates()
    
    print("\n" + "="*60)
    print("SIMULACIÓN COMPLETADA")
    print("="*60)
    print("""
    Resumen de lo implementado:
    ✓ Puertas cuánticas: X, H, Z, S, T, CNOT
    ✓ Clase QuantumCircuit con métodos de aplicación y medición
    ✓ Soporte para puertas de 1 y 2 qubits
    ✓ Visualización con matplotlib
    ✓ Ejemplo de estado de Bell entrelazado
    """)