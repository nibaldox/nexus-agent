# Visualización 3: Evolución de Qubits por Empresa (2020-2025)

## Comparación del Número de Qubits (2020-2025)

```mermaid
xychart-beta
    title "Evolución de Qubits por Empresa (2020-2025)"
    x-axis [2020, 2021, 2022, 2023, 2024, 2025]
    y-axis "Número de Qubits (escala log)" 10 --> 2000
    line [65, 65, 127, 433, 1121, 100000]
    line [53, 72, 433, 133, 105, 500]
    line [11, 11, 20, 28, 32, 64]
    line [5, 7, 11, 56, 56, 100]
    line [6, 8, 24, 80, 1225, 10000]
    line [0, 0, 0, 0, 214, 1000]
```
*Nota: IBM=azul, Google=naranja, IonQ=verde, Quantinuum=rojo, Atom Computing=morado, Xanadu=cyan*

---

## Datos de Evolución (Tabla)

| Empresa | 2020 | 2021 | 2022 | 2023 | 2024 | 2025 Proy |
|---------|------|------|------|------|------|-----------|
| **IBM** | 65 | 65 | 127 | 433 | 1121 | 100K+ (virtual) |
| **Google** | 53 | 72 | 433 | 133 | 105 | 500+ |
| **IonQ** | 11 | 11 | 20 | 28 | 32 | 64 |
| **Quantinuum** | 5 | 7 | 11 | 56 | 56 | 100 |
| **Atom Computing** | 6 | 8 | 24 | 80 | 1225 | 10K+ |
| **Xanadu** | 0 | 0 | 0 | 0 | 214 | 1000+ |

---

## Proyección de Qubits Lógicos vs Físicos

```mermaid
%%{init: {'theme': 'base', 'themeVariables': { 'primaryColor': '#4a90d9', 'edgeLabelBackground':'#ffffff', 'tertiaryColor': '#f5f5f5'}}}%%
graph LR
    subgraph "Evolución hacia Qubits Lógicos"
        A[Qubits Físicos<br/>2024: 100-1000] --> B[Errores de Qubit<br/>Tasa: 0.1-1%]
        B --> C[Códigos Correctores<br/>Surface Code]
        C --> D[Qubits Lógicos<br/>2025: 10-100]
        D --> E[Computación Tolerante<br/>2030: 1000+]
        
        A1[IBM Heron<br/>133 qubits] --> D
        A2[Google Willow<br/>105 qubits] --> D
        A3[Atom Comp<br/>1225 qubits] --> D
    end
    
    style A fill:#4a90d9,stroke:#2c5aa0,color:#fff
    style D fill:#27ae60,stroke:#1e8449,color:#fff
    style E fill:#9b59b6,stroke:#7d3c98,color:#fff
```

---

## Roadmap de Error Correction (2024-2030)

```mermaid
pie showData
    title "Proporción de Recursos para Error Correction"
    "Physical qubits for 1 logical" : 1000
    "Overhead codes" : 500
    "Benchmarking" : 200
    "Physical qubits (2024)" : 100
```

*El objetivo 2030: 1000+ qubits lógicos con error rate < 10⁻¹²*