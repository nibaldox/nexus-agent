# 🌤️ BRIEF DE VISUALIZACIÓN: Clima Madrid

## Datos de Entrada

### 📅 Período de Análisis
- **Fecha de inicio:** Domingo 26 de enero de 2025
- **Pronóstico:** 7 días (hasta sábado 1 de febrero de 2025)

---

## 1. Títulos del Gráfico

### Título Principal (Recomendado)
```
🌧️ Pronóstico del Clima - Madrid
Semana del 26 enero al 1 febrero 2025
```

### Títulos Alternativos
| Opción | Descripción |
|--------|-------------|
| A | "Madrid: Alerta de Lluvia - 90-100% probabilidad hasta el sábado" |
| B | "Evolución Térmica y Probabilidad de Precipitación - Madrid" |
| C | "Clima Madrid: 6 de 7 días con Lluvia Probable" |
| D | "Semana Lluviosa en Madrid: Temperaturas entre 3°C y 14°C" |

---

## 2. Tipo de Gráfico Recomendado

### **Gráfico Combinado: Line Chart + Bar Chart**

```
┌─────────────────────────────────────────────────────────────┐
│                                                             │
│   ████████████████████  100%                                │
│   ████████████████████  Prob. Lluvia (%)                    │
│   ████████████████████                                      │
│   ████████████████████   ─── Temperatura Máxima (°C)        │
│   ████████████████████   ╍╍ Temperatura Mínima (°C)         │
│   ████████                                                   │
│   ████████                                                   │
│   ─────────                                                 │
│   Dom  Lun  Mar  Mié  Jue  Vie  Sáb                         │
│    26   27   28   29   30   31    1                         │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### Justificación del Tipo de Gráfico

| Criterio | Evaluación | Puntuación |
|----------|------------|------------|
| Comparación temporal | Muestra evolución de 7 días | ⭐⭐⭐⭐⭐ |
| Múltiples variables | 3 series de datos (Tmax, Tmin, ProbLluvia) | ⭐⭐⭐⭐⭐ |
| Relación entre variables | Correlación visual precipitación-temperatura | ⭐⭐⭐⭐ |
| Claridad de interpretación | Eje dual permite leer ambos rangos | ⭐⭐⭐⭐⭐ |
| Complejidad de datos | Requiere mostrar tendencias + magnitudes | ⭐⭐⭐⭐ |

### Alternativas Consideradas

| Tipo | Uso | Rechazo |
|------|-----|---------|
| **Area Chart** | Tendencia de precipitación acumulada | ❌ Pierde detalle de categorías diarias |
| **Scatter Plot** | Correlación T° vs ProbLluvia | ❌ No muestra dimensión temporal |
| **Heatmap** | Intensidad de lluvia por día/hora | ❌ Excesivo para datos diarios |

---

## 3. Especificación de Ejes

### Eje X (Horizontal) - Días
```
x_values = ["Dom 26", "Lun 27", "Mar 28", "Mié 29", "Jue 30", "Vie 31", "Sáb 1"]
```

| Atributo | Valor |
|----------|-------|
| **Formato** | Día + Fecha (abreviado) |
| **Espaciado** | Uniforme (categoría discreta) |
| **Rotación** | 0° (horizontal) |
| **Orden** | Cronológico (izquierda a derecha) |

### Eje Y Izquierdo - Temperatura (°C)
```
y_temp_values = [10, 11, 11, 12, 14, 12, 12]  # Máximas
y_temp_min_values = [3, 4, 3, 4, 5, 4, 3]      # Mínimas
```

| Atributo | Valor |
|----------|-------|
| **Rango** | 0°C a 16°C (con margen de seguridad) |
| **Intervalo** | 2°C |
| **Unidad** | Grados Celsius (°C) |
| **Color de línea** | Naranja (máxima), Azul frío (mínima) |

### Eje Y Derecho - Probabilidad de Lluvia (%)
```
y_rain_values = [90, 100, 100, 90, 35, 90, 100]
```

| Atributo | Valor |
|----------|-------|
| **Rango** | 0% a 100% |
| **Intervalo** | 20% |
| **Unidad** | Porcentaje (%) |
| **Tipo visual** | Barras verticales |
| **Color de barra** | Azultransparente (rgba) |

---

## 4. Notas Explicativas y Contexto Visual

### 📌 Notas Técnicas

```
NOTAS:
─────────────────────────────────────────────────────────────
• Datos actualizados: 26 enero 2025, 08:00 UTC
• Fuente: AEMET (Agencia Estatal de Meteorología)
• Probabilidad expresada como % de certeza de precipitación
• Temperaturas en grados Celsius (°C)
─────────────────────────────────────────────────────────────
```

### 📊 Contexto Visual

| Elemento | Descripción |
|----------|-------------|
| **Encabezado** | Semilla + Período de pronóstico |
| **Leyenda** | Posición superior con iconos diferenciados |
| **Tooltips** | Información detallada al hover |
| **Grid lines** | Horizontales suaves (opacidad 0.3) |
| **Anotaciones** | Día outlier (Jueves 30: 35% prob) |

### 🎯 Highlights Visuales

```
┌─────────────────────────────────────────────────────────┐
│  ⚠️  DESTAQUES DEL PRONÓSTICO                            │
├─────────────────────────────────────────────────────────┤
│  🔴 JUEVES 30: Único día sin probabilidad alta (35%)    │
│  🔵 VIERNES 31: Lluvia intensa retorna (90%)            │
│  🟠 JUEVES 30: Día más cálido (14°C máx)                │
│  🔵 SÁBADO 1: Peak de probabilidad (100%)               │
│  🟤 DOMINGO/LUNES/MARTES: Mínimas frías (3-4°C)         │
└─────────────────────────────────────────────────────────┘
```

---

## 5. Estrategia para Múltiples Series de Datos

### A) Temperatura Máxima (Line Chart)
```javascript
{
  type: 'line',
  data: [10, 11, 11, 12, 14, 12, 12],
  label: 'Temperatura Máxima (°C)',
  borderColor: '#FF6B35',      // Naranja cálido
  backgroundColor: 'transparent',
  borderWidth: 3,
  tension: 0.3,                // Curva suave
  pointRadius: 5,
  pointHoverRadius: 7
}
```

### B) Temperatura Mínima (Line Chart)
```javascript
{
  type: 'line',
  data: [3, 4, 3, 4, 5, 4, 3],
  label: 'Temperatura Mínima (°C)',
  borderColor: '#4ECDC4',      // Azul verdoso frío
  backgroundColor: 'transparent',
  borderWidth: 3,
  borderDash: [5, 5],          // Línea punteada
  tension: 0.3,
  pointRadius: 4,
  pointHoverRadius: 6
}
```

### C) Probabilidad de Lluvia (Bar Chart)
```javascript
{
  type: 'bar',
  data: [90, 100, 100, 90, 35, 90, 100],
  label: 'Probabilidad Lluvia (%)',
  backgroundColor: 'rgba(52, 152, 219, 0.6)',
  borderColor: 'rgba(52, 152, 219, 1)',
  borderWidth: 1,
  yAxisID: 'y1'                // Eje secundario
}
```

### 📈 Estrategia de Superposición

```
Y (Derecho 100%)
│    ████  ████  ████  ████  ███  ████  ████
│    ████  ████  ████  ████  ███  ████  ████
│    ████  ████  ████  ████  ███  ████  ████
│    ████  ████  ████  ████  ███  ████  ████
│    ───── ───── ───── ───── ──── ───── ─────
│    ╍╍╍   ╍╍╍   ╍╍╍   ╍╍╍   ╍╍╍   ╍╍╍   ╍╍╍
│    ╍╍╍   ╍╍╍   ╍╍╍   ╍╍╍   ╍╍╍   ╍╍╍   ╍╍╍
Y (Izquierdo °C)
│    ●    ●    ●    ●    ●    ●    ●         Máxima
│         ○    ○    ○    ○    ○    ○    ○    Mínima
└───────────────────────────────────────────────── X
      Dom  Lun  Mar  Mie  Jue  Vie  Sab
```

---

## 6. Paleta de Colores Sugerida

### 🎨 Paleta Semántica del Clima

| Elemento | Color Hex | RGB | Uso |
|----------|-----------|-----|-----|
| **Lluvia/Prec.** | `#3498DB` | 52, 152, 219 | Barras de precipitación |
| **Lluvia Osc.** | `#2980B9` | 41, 128, 185 | Borde barras |
| **T° Máxima** | `#FF6B35` | 255, 107, 53 | Línea temperatura alta |
| **T° Mínima** | `#4ECDC4` | 78, 205, 196 | Línea temperatura baja |
| **Alto Riesgo** | `#E74C3C` | 231, 76, 60 | Prob > 90% |
| **Medio Riesgo** | `#F39C12` | 243, 156, 18 | Prob 50-89% |
| **Bajo Riesgo** | `#27AE60` | 39, 174, 96 | Prob < 50% |
| **Fondo claro** | `#F8F9FA` | 248, 249, 250 | Canvas |
| **Texto** | `#2C3E50` | 44, 62, 80 | Labels y títulos |

### 🌈 Gradiente para Probabilidad de Lluvia

```css
/* Barras con gradiente vertical */
background: linear-gradient(
  to bottom,
  rgba(52, 152, 219, 0.9) 0%,
  rgba(52, 152, 219, 0.6) 100%
);
```

---

## 7. Indicadores Visuales y Elementos Iconográficos

### 🏷️ Iconos por Condición Climática

| Día | Condición | Icono Sugerido | Color |
|-----|-----------|----------------|-------|
| Dom 26 | Lluvia débil | 🌧️ | Azul |
| Lun 27 | Lluvia moderada | 🌧️🌧️ | Azul oscuro |
| Mar 28 | Lluvia moderada | 🌧️🌧️ | Azul oscuro |
| Mié 29 | Lluvia | 🌧️ | Azul |
| Jue 30 | Parcialmente nuboso | ⛅ | Amarillo/Nublado |
| Vie 31 | Lluvia | 🌧️ | Azul |
| Sáb 1 | Chubascos | 🌦️ | Azul claro |

### 📍 Indicadores de Tendencia

```
┌─────────────────────────────────────────────────────────┐
│  LEYENDA DE ICONOS                                      │
├─────────────────────────────────────────────────────────┤
│  🌧️  = Lluvia (probabilidad 80-100%)                   │
│  🌦️  = Chubasco / Lluvia ligera                        │
│  ⛅   = Parcialmente nuboso                             │
│  ☀️   = Despejado                                       │
│  ─────────────────────────────────────────────────────  │
│  ▲  = Aumento de temperatura vs día anterior           │
│  ▼  = Disminución de temperatura vs día anterior       │
│  ●  = Estable                                          │
└─────────────────────────────────────────────────────────┘
```

### 🎯 Sistema de Alertas Visuales

| Nivel | Probabilidad | Color | Efecto Visual |
|-------|--------------|-------|---------------|
| **CRÍTICO** | 100% | Rojo (#E74C3C) | Borde grueso + Parpadeo suave |
| **ALTO** | 90-99% | Naranja (#F39C12) | Borde medio |
| **MODERADO** | 50-89% | Amarillo (#F1C40F) | Borde sutil |
| **BAJO** | < 50% | Verde (#27AE60) | Sin borde |

---

## 8. Resumen de Configuración Chart.js

```javascript
const weatherChartConfig = {
  type: 'bar', // Base type
  data: {
    labels: ['Dom 26', 'Lun 27', 'Mar 28', 'Mié 29', 'Jue 30', 'Vie 31', 'Sáb 1'],
    datasets: [
      {
        type: 'line',
        label: 'T° Máxima',
        data: [10, 11, 11, 12, 14, 12, 12],
        borderColor: '#FF6B35',
        yAxisID: 'y',
        tension: 0.3
      },
      {
        type: 'line',
        label: 'T° Mínima',
        data: [3, 4, 3, 4, 5, 4, 3],
        borderColor: '#4ECDC4',
        borderDash: [5, 5],
        yAxisID: 'y',
        tension: 0.3
      },
      {
        type: 'bar',
        label: 'Prob. Lluvia %',
        data: [90, 100, 100, 90, 35, 90, 100],
        backgroundColor: 'rgba(52, 152, 219, 0.6)',
        yAxisID: 'y1'
      }
    ]
  },
  options: {
    scales: {
      y: {
        type: 'linear',
        position: 'left',
        title: { display: true, text: 'Temperatura (°C)' },
        min: 0,
        max: 16
      },
      y1: {
        type: 'linear',
        position: 'right',
        title: { display: true, text: 'Probabilidad (%)' },
        min: 0,
        max: 100,
        grid: { drawOnChartArea: false }
      }
    }
  }
};
```

---

## ✅ Checklist de Implementación

| Item | Estado | Prioridad |
|------|--------|-----------|
| Eje dual Y (Temperatura + Probabilidad) | ⬜ Pendiente | ALTA |
| 3 Series de datos superpuestas | ⬜ Pendiente | ALTA |
| Iconos de condición por día | ⬜ Pendiente | MEDIA |
| Tooltips informativos | ⬜ Pendiente | MEDIA |
| Gradiente de color en barras | ⬜ Pendiente | BAJA |
| Anotación día outlier (Jue 30) | ⬜ Pendiente | MEDIA |
| Responsive design | ⬜ Pendiente | ALTA |

---

## 📁 Metadatos del Artefacto

| Campo | Valor |
|-------|-------|
| **Nombre archivo** | `brief_clima_madrid.md` |
| **Fecha creación** | 26 enero 2025 |
| **Versión** | 1.0 |
| **Autor** | Data Intelligence Lead |
| **Estado** | Listo para implementación |
| **Ruta** | `/artifacts/data_intelligence_lead/` |

---

*Brief generado para visualización con ChartTools - Madrid Weather Forecast Week 4*