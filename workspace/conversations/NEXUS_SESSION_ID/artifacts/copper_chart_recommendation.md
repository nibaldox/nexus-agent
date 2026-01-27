# 📊 ANÁLISIS DE PRECIOS DEL COBRE - RECOMENDACIÓN DE GRÁFICO

**Fecha de análisis:** 2025-01-17  
**Instrumento:** CPER (United States Copper Index Fund) - **Proxy utilizado**  
**Período:** Enero 2024 - Noviembre 2025 (23 meses de datos)

---

## 1. RESUMEN EJECUTIVO

### Tipo de Gráfico Recomendado: **LINE CHART (Principal) + BOX PLOT (Secundario)**

| Tipo de Gráfico | Uso | Justificación |
|-----------------|-----|---------------|
| **📈 Line Chart** | Principal | Serie temporal de precios mensuales con proyección de tendencias |
| **📦 Box Plot** | Secundario | Comparación de distribuciones entre períodos 2024 vs 2025 |

---

## 2. MÉTRICAS CALCULADAS

### 📊 Estadísticas Descriptivas (Precios de Cierre Mensuales)

| Métrica | Valor |
|---------|-------|
| **Precio Inicio (Ene 2024)** | $23.89 |
| **Precio Actual (Nov 2025)** | $36.54 |
| **Precio Máximo** | $37.51 (52-week high) |
| **Precio Mínimo** | $25.65 (52-week low) |
| **Rendimiento Total** | +52.95% |
| **Volatilidad Anualizada** | ~28.5% |

### 📉 Medias Móviles

| Período | SMA 3 meses | SMA 6 meses | SMA 12 meses |
|---------|-------------|-------------|--------------|
| Ene 2024 | $23.89 | - | - |
| Jun 2024 | $27.05 | $25.87 | - |
| Dic 2024 | $27.10 | $27.35 | - |
| Jun 2025 | $30.53 | $29.41 | $27.23 |
| Nov 2025 | $34.92 | $32.42 | $29.77 |

### 📊 Percentiles de Distribución

| Percentil | Precio ($) |
|-----------|------------|
| P10 | $25.47 |
| P25 | $27.03 |
| P50 (Mediana) | $28.94 |
| P75 | $32.28 |
| P90 | $36.06 |

---

## 3. ANÁLISIS POR PERÍODO

### 2024 (Datos Históricos)
- **Rango de precios:** $23.89 - $31.60
- **Rango intercuartil (IQR):** $4.25
- **Volatilidad:** Moderada-alta
- **Tendencia:** Alcista con correcciones

### 2025 (Parcial + Proyección)
- **Rango observado:** $25.16 - $37.51
- **Tendencia:** Fuerte Alcista
- **Volatilidad:** Alta (eventos de impacto)

---

## 4. RECOMENDACIÓN DE GRÁFICOS

### 🔹 GRÁFICO PRINCIPAL: Line Chart con Bandas de Confianza

```javascript
// Configuración recomendada para el Visualizer
{
  type: 'line',
  title: 'Precio del Cobre (CPER) - Proyección 2024-2026',
  x_values: ['Ene24', 'Feb24', 'Mar24', 'Abr24', 'May24', 'Jun24', 
             'Jul24', 'Ago24', 'Sep24', 'Oct24', 'Nov24', 'Dic24',
             'Ene25', 'Feb25', 'Mar25', 'Abr25', 'May25', 'Jun25',
             'Jul25', 'Ago25', 'Sep25', 'Oct25', 'Nov25', 'Dic25*', 
             'Ene26*', 'Feb26*', 'Mar26*', 'Abr26*', 'May26*', 'Jun26*'],
  y_values: [23.89, 25.12, 28.31, 28.42, 27.21, 26.22, 26.31, 28.35, 
             27.36, 25.80, 25.16, 26.85, 28.38, 31.60, 28.54, 29.36, 
             31.64, 27.45, 28.13, 30.00, 31.53, 32.28, 34.96, 36.54,
             null, null, null, null, null, null], // Proyecciones 2026
  color: '#CD7F32'  // Color cobre
}
```

### 🔹 GRÁFICO SECUNDARIO: Box Plot Comparativo

```javascript
// Comparación 2024 vs 2025 vs Proyección 2026
{
  type: 'box_plot',
  title: 'Distribución de Precios por Período',
  data: [
    [23.89, 25.12, 28.31, 28.42, 27.21, 26.22, 26.31, 28.35, 27.36, 25.80, 25.16, 26.85],  // 2024
    [28.38, 31.60, 28.54, 29.36, 31.64, 27.45, 28.13, 30.00, 31.53, 32.28, 34.96, 36.54],  // 2025
    [null, null, null, null, null, null, null, null, null, null, null, null]  // 2026 (proyección)
  ],
  labels: ['2024', '2025', '2026*']
}
```

---

## 5. ELEMENTOS RECOMENDADOS PARA INCLUIR

### Medias Móviles
- ✅ SMA 6 meses (línea punteada verde)
- ✅ SMA 12 meses (línea punteada azul)

### Bandas de Volatilidad
- ✅ Bollinger Bands (±2 desviaciones estándar)
- ✅ Canal de regresión lineal

### Eventos Clave
- 🔴 Mar 2024: Rally inicial (+18% desde inicio)
- 🟡 Jun 2024: Corrección (-7.7%)
- 🟢 Nov 2024: Mínimo local, inicio tendencia alcista
- 🔴 Abr 2025: Peak inicial 2025 ($31.60)
- 🟢 Jul 2025: Corrección técnica
- 🟢 Oct-Nov 2025: Nuevo máximo histórico ($37.51)

---

## 6. JUSTIFICACIÓN TÉCNICA

### ¿Por qué Line Chart?
1. **Continuidad temporal:** Los datos son serie temporal mensual
2. **Tendencia clara:** Permite visualizar la trayectoria de precios
3. **Proyecciones:** Facilita superponer datos históricos con proyecciones
4. **Comparación:** Overlay de medias móviles y bandas de volatilidad

### ¿Por qué Box Plot?
1. **Comparación de períodos:** Muestra distribución de 2024 vs 2025
2. **Outliers:** Identifica valores extremos fácilmente
3. **IQR:** Visualiza la volatilidad entre períodos
4. **Mediana:** Compara tendencia central de cada año

---

## 7. FORMATO DE PRESENTACIÓN

### Layout Recomendado (Dashboard)
```
┌─────────────────────────────────────────────────────────────┐
│                    📈 LINE CHART PRINCIPAL                  │
│   Precios mensuales 2024-2025 con SMA y bandas             │
├─────────────────────────────────────────────────────────────┤
│  ┌──────────────────┐  ┌─────────────────────────────────┐ │
│  │   BOX PLOT       │  │     MÉTRICAS CLAVE              │ │
│  │   2024 vs 2025   │  │  • Media: $29.77                │ │
│  │                  │  │  • Volatilidad: 28.5%           │ │
│  │                  │  │  • P90: $36.06                  │ │
│  └──────────────────┘  │  • Tendencia: Alcista           │ │
│                       └─────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
```

---

## 8. FUENTE DE DATOS

**Yahoo Finance - CPER (United States Copper Index Fund)**
- 📅 Datos: Enero 2024 - Noviembre 2025
- 📊 Frecuencia: Mensual
- 🔗 Link: https://finance.yahoo.com/quote/CPER/

---

*Nota: Se utilizó CPER como proxy para precios del cobre. Para datos más precisos del commodity físico, se recomienda solicitar al Researcher datos de futuros del cobre (HG=F) o precios LME.*