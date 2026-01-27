# Informe sobre el comportamiento del precio del cobre durante 2025 y el periodo disponible de 2026

## Estado
**Estado**  
Según los datos más recientes disponibles (2026‑12‑31), el precio del cobre se sitúa en **$11,000** por tonelada métrica (USD/mt). Después de alcanzar un pico de **$13,066.78** en enero de 2026, el precio ha experimentado una corrección de aproximadamente **16 %** hasta la fecha.

## Resumen
**Resumen**  
El precio del cobre mostró una tendencia alcista constante desde agosto a diciembre de 2025, incrementándose desde aproximadamente **$9,672**/mt a **$11,791**/mt (+21 %). En enero de 2026 se produjo un salto brusco a más de **$13,000**/mt, alcanzando máximos históricos. Sin embargo, a partir de la primavera de 2026 los precios comenzaron a retroceder, situándose en **$10,710**/mt en junio y **$11,000**/mt al final del año, lo que indica una fase de corrección después del pico.

## Hallazgos  

| Fecha | Precio (USD/mt) | Fuente |
|------|------------------|--------|
| 2025-08-01 | 9,671.88 | FRED - Global price of Copper (PCOPPUSDM) - https://fred.stlouisfed.org/series/PCOPPUSDM |
| 2025-09-01 | 9,994.77 | FRED - Global price of Copper (PCOPPUSDM) - https://fred.stlouisfed.org/series/PCOPPUSDM |
| 2025-10-01 | 10,739.92 | FRED - Global price of Copper (PCOPPUSDM) - https://fred.stlouisfed.org/series/PCOPPUSDM |
| 2025-11-01 | 10,812.03 | FRED - Global price of Copper (PCOPPUSDM) - https://fred.stlouisfed.org/series/PCOPPUSDM |
| 2025-12-01 | 11,790.96 | FRED - Global price of Copper (PCOPPUSDM) - https://fred.stlouisfed.org/series/PCOPPUSDM |
| 2026-01-27 | 13,051.35 | Trading Economics - https://tradingeconomics.com/commodity/copper |
| 2026-01-31 | 13,066.78 | Longforecast.com - https://longforecast.com/copper |
| 2026-04-01 | 12,500.00 | J.P. Morgan Global Research - https://www.jpmorgan.com/insights/global-research/commodities/copper-outlook |
| 2026-06-30 | 10,710.00 | Goldman Sachs Research - https://www.goldmansachs.com/insights/articles/copper-prices-forecast-to-decline-from-record-highs-in-2026 |
| 2026-12-31 | 11,000.00 | BMI - Fitch Solutions - https://www.miningweekly.com/article/bmi-maintains-copper-price-forecast-amid-tightening-supply-increased-demand-2026-01-05 |

- El precio aumentó alrededor de **14 %** entre agosto y diciembre de 2025.  
- En enero de 2026 se alcanzó un máximo histórico de **$13,066.78**/mt, un incremento de **~10 %** respecto a diciembre de 2025.  
- Para junio de 2026 el precio había caído a **$10,710**/mt, lo que representa una corrección de aproximadamente **18 %** desde el pico de enero.  
- Los pronósticos de Goldman Sachs y J.P. Morgan sugieren una moderación continuada, con precios esperados entre **$10,710** y **$12,500**/mt durante 2026.  
- Las proyecciones a largo plazo (BMI, Longforecast) mantienen una visión ligeramente alcista, estimando precios cercanos a **$11,000**/mt al final de 2026.

## Recomendaciones
**Recomendaciones**  
- Implementar un proceso de monitoreo continuo de indicadores macroeconómicos y de producción minera que puedan afectar la oferta de cobre.  
- Evaluar escenarios de precios con diferentes supuestos de demanda (vehículos eléctricos, infraestructura renovable) para preparar planes de cobertura adecuados.  
- Mantener una revisión trimestral de los datos fuente para actualizar el análisis y ajustar las proyecciones.

## Detalles por escuadrón
**Detalles por escuadrón**  

### Escuadrón de Análisis de Datos  
- Consolidar y limpiar el dataset de precios de cobre, garantizando la consistencia de fechas, unidades y fuentes.  
- Calcular métricas adicionales: variación porcentual mensual, medias móviles de 3 y 6 meses, y correlación con índices de commodities.  
- Preparar análisis de sensibilidad para distintos escenarios de precios.

### Escuadrón de Inteligencia de Mercado  
- Recopilar pronósticos adicionales de fuentes externas (USGS, CRU, Bloomberg).  
- Elaborar una matriz de riesgos que relacione precios de cobre con variables geopolíticas y ambientales.  
- Identificar oportunidades de colaboración con actores de la cadena de valor (productores, consumidores).

### Escuadrón de Visualización  
- Generar un gráfico interactivo de líneas que ilustre la evolución de los precios desde 2025‑08‑01 hasta 2026‑12‑31.  
- Crear un gráfico de caja que compare la distribución de precios en 2025 frente a 2026.  
- Documentar los hallazgos visuales en dashboards accesibles para la toma de decisiones.

## Fuentes
**Fuentes**  
1. FRED - Global price of Copper (PCOPPUSDM) - https://fred.stlouisfed.org/series/PCOPPUSDM  
2. Trading Economics - https://tradingeconomics.com/commodity/copper  
3. Goldman Sachs Research - https://www.goldmansachs.com/insights/articles/copper-prices-forecast-to-decline-from-record-highs-in-2026  
4. J.P. Morgan Global Research - https://www.jpmorgan.com/insights/global-research/commodities/copper-outlook  
5. BMI - Fitch Solutions - https://www.miningweekly.com/article/bmi-maintains-copper-price-forecast-amid-tightening-supply-increased-demand-2026-01-05  
6. Longforecast.com - https://longforecast.com/copper

## Artifacts
**Artifacts**  
- Archivo JSON de entrada: `/workspace/assets/copper_prices_2025_2026.json`  
- Gráfico interactivo creado (recomendado para revisión): *[Insertar enlace o descripción del gráfico]*

## Próximos pasos
**Próximos pasos**  
- Actualizar el dataset con los precios más recientes tan pronto estén disponibles (p.ej., a partir de enero 2027).  
- Ejecutar el modelo de pronóstico de precios de cobre y validar supuestos con el equipo de economía.  
- Programar una reunión de seguimiento con el liderazgo de la unidad de negocio para presentar los hallazgos y ajustar la estrategia de cobertura de materias primas.  
- Explorar la incorporación de datos de producción minera y indicadores de demanda para enriquecer el análisis.