# Visualización 1: Mapa del Ecosistema de Computación Cuántica

## Posicionamiento por Tipo de Qubit (2024-2025)

```mermaid
mindmap
  root((ECOSISTEMA<br/>CUÁNTICO))
    SUPERCONDUCTING
      ::icon(fa fa-bolt)
      IBM
        ::icon(fa fa-server)
        Eagle/Osprey
        Heron (2024)
        Kookaburra (2025)
      Google
        ::icon(fa fa-google)
        Sycamore
        Willow (2024)
      Rigetti
        ::icon(fa fa-microchip)
        Aspen Series
      Amazon
        ::icon(fa fa-amazon)
        Braket
    TRAPPED_IONS
      ::icon(fa fa-atom)
      IonQ
        ::icon(fa fa-database)
        Forte/Aria
        Hybrid trapped ion
      Quantinuum
        ::icon(fa fa-flask)
        H2 (56 qubits)
        System Model H2
      Alpine Quantum
        ::icon(fa fa-cube)
        AQT PINE
    PHOTONIC
      ::icon(fa fa-lightbulb)
      Xanadu
        ::icon(fa fa-star)
        Borealis (214 qubits)
        Gaussian Boson Sampler
      PsiQuantum
        ::icon(fa fa-eye)
        Fault-tolerant prototype
      Cambridge Quantum
        ::icon(fa fa-random)
        Tiet+Ebbets merger
    SILICON
      ::icon(fa fa-microchip)
      Intel
        ::icon(fa fa-desktop)
        Tunnel Falls
        Spin qubits
      QuTech
        ::icon(fa fa-university)
        Delft spin qubits
    NEUTRAL_ATOMS
      ::icon(fa fa-asterisk)
      Pasqal
        ::icon(fa fa-atom)
        CoolQure
      QuEra
        ::icon(fa fa-network-wired)
        Aquila (256 qubits)
      Atom Computing
        ::icon(fa fa-cubes)
        1225 qubits (2024)
```

## Matriz de Posicionamiento Competitivo

```mermaid
quadrantChart
    title "Posicionamiento de Plataformas Cuánticas"
    x-axis "Aplicación Comercial -->" to "Investigación Fundamental"
    y-axis "Madura (2024) -->" to "Emerging (2025+)"
    quadrant-1 "Líderes de Mercado"
    quadrant-2 "Especialistas"
    quadrant-3 "New Entrants"
    quadrant-4 "Visionarios"
    "Google Willow": [0.85, 0.75]
    "IBM Heron": [0.80, 0.70]
    "IonQ Aria": [0.70, 0.85]
    "Quantinuum H2": [0.65, 0.80]
    "Xanadu Borealis": [0.55, 0.90]
    "Pasqal CoolQure": [0.45, 0.75]
    "Atom Comp 1225": [0.40, 0.95]
    "PsiQuantum": [0.35, 0.88]
    "Microsoft Majorana": [0.30, 0.95]
    "Rigetti": [0.60, 0.55]
```

---

*Nota: El eje X representa el madurez hacia aplicaciones comerciales vs investigación. El eje Y indica la madurez tecnológica actual vs potencial emergente.*