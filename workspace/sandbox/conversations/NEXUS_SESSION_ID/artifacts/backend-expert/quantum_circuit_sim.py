"""
=============================================================
SIMULADOR DE CIRCUITO CUÁNTICO DE 2 QUBITS
Implementación usando NumPy para el Backend Expert
=============================================================

Nota sobre convención de qubits:
- El sistema se representa con vector de estado de dimensión 4
- Orden de estados base: |00⟩, |01⟩, |10⟩, |11⟩ (qubit 1 = MSB, qubit 0 = LSB)
- Puerta H en qubit i aplica Hadamard a ese qubit específico
- CNOT(control, target) invierte target si control = |1⟩
"""

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from typing import Union, Dict

# ============================================================================
# DEFINICIÓN DE PUERTAS CUÁNTICAS BÁSICAS
# ============================================================================

class QuantumGates:
    """
    Colección de puertas cuánticas fundamentales.
    Todas las matrices están normalizadas y representan operaciones unitarias.
    """
    
    # ----- Puerta X (NOT cuántico) -----
    # Invierte los estados |0⟩ ↔ |1⟩
    # Matriz: [[0, 1], [1, 0]]
    X = np.array([[0, 1], 
                  [1, 0]], dtype=complex)
    
    # ----- Puerta H (Hadamard) -----
    # Crea superposición equiprobable: H|0⟩ = (|0⟩ + |1⟩)/√2
    # Matriz: (1/√2)[[1, 1], [1, -1]]
    H = (1 / np.sqrt(2)) * np.array([[1, 1], 
                                     [1, -1]], dtype=complex)
    
    # ----- Puerta Z (Pauli-Z) -----
    # Aplica fase -1 al estado |1⟩: Z|0⟩ = |0⟩, Z|1⟩ = -|1⟩
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
    # CNOT(control, target): invierte target si control = |1⟩
    # Con qubit 1 como control (MSB) y qubit 0 como objetivo (LSB):
    # |00⟩ → |00⟩, |01⟩ → |01⟩, |10⟩ → |11⟩, |11⟩ → |10⟩
    CNOT = np.array([
        [1, 0, 0, 0],  # |00⟩ → |00⟩
        [0, 1, 0, 0],  # |01⟩ → |01⟩
        [0, 0, 0, 1],  # |10⟩ → |11⟩
        [0, 0, 1, 0]   # |11⟩ → |10⟩
    ], dtype=complex)


# ============================================================================
# CLASE PRINCIPAL DEL CIRCUITO CUÁNTICO
# ============================================================================

class QuantumCircuit:
    """
    Simulador de circuito cuántico de 2 qubits.
    
    El sistema se representa mediante un vector de estado de dimensión 4,
    correspondiente a las bases: |00⟩, |01⟩, |10⟩, |11⟩
    
    Donde:
    - El qubit 1 es el más significativo (MSB)
    - El qubit 0 es el menos significativo (LSB)
    
    Attributes:
        state: Vector de estado actual del sistema (complejo, normalizado)
        num_qubits: Número de qubits del circuito (fijo en 2)
    """
    
    def __init__(self, num_qubits: int = 2):
        """
        Inicializa el circuito en el estado base |00⟩.
        
        Args:
            num_qubits: Número de qubits (solo soporta 2 para este simulador)
        """
        self.num_qubits = num_qubits
        
        # Estado inicial |00⟩ = [1, 0, 0, 0]ᵀ
        # Solo el estado base |00⟩ tiene probabilidad 1
        self.state = np.zeros(2 ** num_qubits, dtype=complex)
        self.state[0] = 1.0  # |00⟩ tiene amplitud 1
        
        print(f"[OK] Circuito cuantico inicializado con estado |00>")
        print(f"     Dimension del espacio de Hilbert: {2**num_qubits}")
    
    def apply_gate(self, gate: np.ndarray, target: int, 
                   control: Union[int, None] = None):
        """
        Aplica una puerta cuantica al circuito.
        
        Para puertas de 1 qubit:
        - target = 0: aplica al qubit menos significativo (LSB)
        - target = 1: aplica al qubit mas significativo (MSB)
        
        Para puertas de 2 qubits (CNOT):
        - control: qubit que controla la operacion
        - target: qubit que se invierte si control = |1⟩
        
        Args:
            gate: Matriz de la puerta (2x2 o 4x4)
            target: Indice del qubit objetivo
            control: Indice del qubit de control (None para puertas de 1 qubit)
        """
        # Validacion de qubits
        if target < 0 or target >= self.num_qubits:
            raise ValueError(f"Qubit objetivo invalido: {target}")
        
        if control is not None and (control < 0 or control >= self.num_qubits):
            raise ValueError(f"Qubit de control invalido: {control}")
        
        # Determinar tipo de puerta por su dimension
        if gate.shape == (2, 2):
            # Puerta de 1 qubit
            self._apply_single_qubit_gate(gate, target)
        elif gate.shape == (4, 4):
            # Puerta de 2 qubits
            self._apply_two_qubit_gate(gate, control, target)
        else:
            raise ValueError(f"Dimension de puerta no soportada: {gate.shape}")
    
    def _apply_single_qubit_gate(self, gate: np.ndarray, target: int):
        """
        Aplica una puerta de 1 qubit usando producto tensor de Kronecker.
        
        El qubit 0 es el LSB, el qubit 1 es el MSB.
        
        Para target=0 (LSB): I ⊗ gate
        Para target=1 (MSB): gate ⊗ I
        
        Esto aplica la puerta solo al qubit especificado.
        """
        if target == 0:
            # Puerta en qubit 0 (LSB): I ⊗ gate
            # Ejemplo: si gate = H, I⊗H transforma |10> → (|10> + |11>)/√2
            full_gate = np.kron(np.eye(2, dtype=complex), gate)
        else:  # target == 1
            # Puerta en qubit 1 (MSB): gate ⊗ I
            # Ejemplo: si gate = H, H⊗I transforma |01> → (|01> + |11>)/√2
            full_gate = np.kron(gate, np.eye(2, dtype=complex))
        
        # Evolucion unitaria: |ψ'⟩ = U|ψ⟩
        self.state = full_gate @ self.state
        
        # Normalizar para evitar errores numericos
        norm = np.linalg.norm(self.state)
        if norm > 0:
            self.state /= norm
    
    def _apply_two_qubit_gate(self, gate: np.ndarray, control: int, target: int):
        """
        Aplica una puerta de 2 qubits (CNOT).
        
        La matriz 4x4 ya viene predefinida para el orden |00⟩, |01⟩, |10⟩, |11⟩
        """
        if control == 0 and target == 1:
            # CNOT(0→1): qubit 0 (LSB) controla, qubit 1 (MSB) es objetivo
            # Invierte qubit 1 cuando qubit 0 = |1⟩
            cnot_01 = np.array([
                [1, 0, 0, 0],  # |00> → |00>
                [0, 0, 0, 1],  # |01> → |11> (qubit0=1, qubit1 flip)
                [0, 0, 1, 0],  # |10> → |10> (qubit0=0)
                [0, 1, 0, 0]   # |11> → |01> (qubit0=1, qubit1 flip)
            ], dtype=complex)
            self.state = cnot_01 @ self.state
        elif control == 1 and target == 0:
            # CNOT(1→0): qubit 1 (MSB) controla, qubit 0 (LSB) es objetivo
            # Invierte qubit 0 cuando qubit 1 = |1⟩ (matriz estandar CNOT)
            self.state = QuantumGates.CNOT @ self.state
        else:
            raise ValueError("CNOT requiere qubits 0 y 1")
        
        # Normalizar
        norm = np.linalg.norm(self.state)
        if norm > 0:
            self.state /= norm
    
    def apply_cnot(self, control: int, target: int):
        """
        Metodo conveniente para aplicar CNOT.
        
        Args:
            control: Indice del qubit de control
            target: Indice del qubit objetivo
        """
        self.apply_gate(QuantumGates.CNOT, target, control)
    
    def measure(self, shots: int = 1000) -> Dict[str, int]:
        """
        Mide el estado cuantico y colapsa al estado medido.
        
        La medicion destruye la superposicion y colapsa a uno
        de los estados base con probabilidad proporcional al
        cuadrado de su amplitud (regla de Born).
        
        Args:
            shots: Numero de veces que se mide
        
        Returns:
            Dictionary con los conteos de cada estado medido
        """
        # Calcular probabilidades: |amplitude|²
        probabilities = np.abs(self.state) ** 2
        
        # Verificar normalizacion
        assert np.isclose(np.sum(probabilities), 1.0), \
            f"Las probabilidades no suman 1: {np.sum(probabilities)}"
        
        # Estados base
        basis_states = ['|00>', '|01>', '|10>', '|11>']
        
        # Simular mediciones
        outcomes = np.random.choice(
            len(self.state), 
            size=shots, 
            p=probabilities
        )
        
        # Contar resultados
        counts = {basis_states[i]: int(np.sum(outcomes == i)) 
                  for i in range(len(self.state))}
        
        # Colapsar al estado mas probable
        collapsed_state_idx = np.argmax(probabilities)
        self.state = np.zeros_like(self.state)
        self.state[collapsed_state_idx] = 1.0
        
        return counts
    
    def get_probabilities(self) -> Dict[str, float]:
        """
        Retorna las probabilidades de cada estado base.
        
        Returns:
            Dictionary con probabilidades de cada estado base
        """
        probabilities = np.abs(self.state) ** 2
        basis_states = ['|00>', '|01>', '|10>', '|11>']
        return {basis_states[i]: float(probabilities[i]) 
                for i in range(len(probabilities))}
    
    def print_state(self):
        """Imprime el estado actual en notacion de Dirac."""
        basis_states = ['|00>', '|01>', '|10>', '|11>']
        state_str = ""
        
        for i, (amp, state) in enumerate(zip(self.state, basis_states)):
            if np.abs(amp) > 1e-10:
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
                state_str += f"{amp_str}|{state[1:3]}>"
        
        print(f"Estado actual: |ψ> = {state_str}")
        print(f"Normalizacion: {np.linalg.norm(self.state):.6f}")


# ============================================================================
# VISUALIZACIÓN DE RESULTADOS
# ============================================================================

def visualize_results(probabilities: Dict[str, float], 
                      counts: Dict[str, int] = None, 
                      title: str = "Probabilidades del Estado Cuantico"):
    """
    Visualiza las probabilidades del circuito cuantico usando matplotlib.
    """
    fig, axes = plt.subplots(1, 2 if counts else 1, figsize=(12, 5))
    
    states = list(probabilities.keys())
    probs = list(probabilities.values())
    colors = ['#3498db', '#2ecc71', '#e74c3c', '#9b59b6']
    
    # Probabilidades teoricas
    ax1 = axes[0] if counts else axes
    bars1 = ax1.bar(states, probs, color=colors, edgecolor='black', linewidth=1.5)
    
    for bar, prob in zip(bars1, probs):
        height = bar.get_height()
        ax1.annotate(f'{prob:.3f}',
                    xy=(bar.get_x() + bar.get_width() / 2, height),
                    xytext=(0, 3),
                    textcoords="offset points",
                    ha='center', va='bottom', fontsize=11, fontweight='bold')
    
    ax1.set_ylabel('Probabilidad', fontsize=12)
    ax1.set_xlabel('Estado Base', fontsize=12)
    ax1.set_title('Probabilidades Teoricas', fontsize=14, fontweight='bold')
    ax1.set_ylim(0, 1.1)
    ax1.axhline(y=1.0, color='gray', linestyle='--', alpha=0.5)
    ax1.grid(axis='y', alpha=0.3)
    
    # Conteos de medicion
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
    plt.close()
    
    print(f"\n[OK] Grafico guardado como 'quantum_results.png'")


# ============================================================================
# EJEMPLO: BELL STATE (|Φ⁺⟩ = (|00⟩ + |11⟩)/√2)
# ============================================================================

def create_bell_state():
    """
    Crea el estado de Bell |Φ⁺⟩ = (|00⟩ + |11⟩)/√2.
    
    El estado de Bell es un estado entrelazado (entangled) maximal.
    No puede escribirse como producto de estados individuales.
    
    Circuito cuantico:
    ┌───┐     
    │ H │     ← Aplicar H al qubit 1 (MSB)
    └─┬─┘     
      │       
    ┌─┴─┐     
    │CNOT│     ← CNOT(1→0): qubit 1 controla, qubit 0 es objetivo
    └───┘     
    
    Paso 1: H en qubit 1 transforma |00⟩ → (|00⟩ + |10⟩)/√2
    Paso 2: CNOT(1→0) transforma |00⟩→|00⟩, |10⟩→|11⟩
    Resultado: (|00⟩ + |11⟩)/√2
    """
    print("\n" + "="*60)
    print("CREANDO ESTADO DE BELL |Φ⁺⟩ = (|00⟩ + |11⟩)/√2")
    print("="*60)
    
    qc = QuantumCircuit(num_qubits=2)
    
    print("\n[Paso 0] Estado inicial:")
    qc.print_state()
    
    # ----- Paso 1: Aplicar Hadamard al qubit 1 (MSB) -----
    # H en qubit 1 (MSB) transforma:
    # |00⟩ → (|00⟩ + |10⟩)/√2
    print("\n[Paso 1] Aplicar puerta H al qubit 1 (MSB):")
    print("  H en qubit 1 (MSB): |00> → (|00> + |10>)/√2")
    qc.apply_gate(QuantumGates.H, target=1)
    qc.print_state()
    
    # ----- Paso 2: Aplicar CNOT(1→0) -----
    # CNOT con qubit 1 como control y qubit 0 como objetivo:
    # |00⟩ → |00⟩ (control=0, no hay cambio)
    # |10⟩ → |11⟩ (control=1, qubit 0 se invierte)
    print("\n[Paso 2] Aplicar CNOT(qubit 1 → qubit 0):")
    print("  CNOT: |00>→|00>, |10>→|11>")
    qc.apply_cnot(control=1, target=0)
    qc.print_state()
    
    # Obtener probabilidades
    probs = qc.get_probabilities()
    print("\n[Analisis] Probabilidades de cada estado base:")
    for state, prob in probs.items():
        print(f"  {state}: {prob:.4f} ({prob*100:.1f}%)")
    
    # Verificar entrelazamiento
    entanglement_check = np.abs(probs['|00>'] - probs['|11>'])
    print(f"\n[Verificacion] |P(|00>) - P(|11>)| = {entanglement_check:.6f}")
    if entanglement_check < 1e-10:
        print("  OK: Estado perfectamente entrelazado (Bell State)")
    
    # Medir multiples veces
    print("\n[Medicion] Realizando 1000 mediciones...")
    counts = qc.measure(shots=1000)
    print("  Resultados de medicion:")
    for state, count in counts.items():
        print(f"    {state}: {count} veces ({count/10:.1f}%)")
    
    # Visualizar
    visualize_results(probs, counts, "Estado de Bell |Φ⁺⟩")
    
    return qc


def demo_other_gates():
    """Demuestra otras puertas cuanticas basicas."""
    print("\n" + "="*60)
    print("DEMOSTRACION DE OTRAS PUERTAS CUANTICAS")
    print("="*60)
    
    # ----- Demo: Puerta X -----
    print("\n[1] PUERTA X (NOT cuantico)")
    print("    X|0> = |1>, X|1> = |0>")
    qc_x = QuantumCircuit(2)
    qc_x.apply_gate(QuantumGates.X, target=0)
    probs = qc_x.get_probabilities()
    print(f"    Resultado: P(|00>)={probs['|00>']:.2f}, P(|10>)={probs['|10>']:.2f}")
    print("    Esperado: |10> con probabilidad 1 (X|0> = |1>)")
    
    # ----- Demo: Puerta H -----
    print("\n[2] PUERTA H (Hadamard) - Superposicion")
    qc_h = QuantumCircuit(2)
    qc_h.apply_gate(QuantumGates.H, target=0)
    probs = qc_h.get_probabilities()
    print(f"    H en qubit 0: P(|00>)={probs['|00>']:.2f}, P(|10>)={probs['|10>']:.2f}")
    print("    Esperado: 50% superposicion entre |00> y |10>")
    
    # ----- Demo: Puerta Z -----
    print("\n[3] PUERTA Z (Pauli-Z) - Cambio de fase")
    print("    Z|0> = |0>, Z|1> = -|1>")
    qc_z = QuantumCircuit(2)
    qc_z.apply_gate(QuantumGates.H, target=0)
    print("    Despues de H en qubit 0:")
    qc_z.print_state()
    qc_z.apply_gate(QuantumGates.Z, target=0)
    print("    Despues de Z en qubit 0:")
    qc_z.print_state()
    probs = qc_z.get_probabilities()
    print(f"    Probabilidades: P(|00>)={probs['|00>']:.2f}, P(|10>)={probs['|10>']:.2f}")
    print("    (Las probabilidades no cambian, solo la fase)")
    
    # ----- Demo: Puertas de fase S y T -----
    print("\n[4] PUERTAS S y T (Phase gates)")
    qc_s = QuantumCircuit(2)
    qc_s.apply_gate(QuantumGates.H, target=0)
    print("    Estado despues de H:")
    qc_s.print_state()
    
    print("    Aplicando S gate:")
    qc_s.apply_gate(QuantumGates.S, target=0)
    qc_s.print_state()
    
    print("    Aplicando T gate:")
    qc_s.apply_gate(QuantumGates.T, target=0)
    qc_s.print_state()


# ============================================================================
# PUNTO DE ENTRADA PRINCIPAL
# ============================================================================

if __name__ == "__main__":
    print("="*60)
    print("           SIMULADOR CUANTICO - 2 QUBITS")
    print("        Implementacion completa con NumPy")
    print("="*60)
    
    # Ejecutar ejemplos
    create_bell_state()
    demo_other_gates()
    
    print("\n" + "="*60)
    print("SIMULACION COMPLETADA")
    print("="*60)
    print("""
    Resumen de lo implementado:
    - Puertas cuanticas: X, H, Z, S, T, CNOT
    - Clase QuantumCircuit con metodos apply_gate y measure
    - Soporte para puertas de 1 y 2 qubits
    - Visualizacion con matplotlib (bar chart)
    - Ejemplo de estado de Bell entrelazado
    """)