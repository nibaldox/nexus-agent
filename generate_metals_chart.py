import matplotlib.pyplot as plt
import matplotlib.ticker as mtick
import numpy as np

# Configurar estilo profesional
plt.style.use('seaborn-v0_8-whitegrid')
plt.rcParams['font.family'] = 'DejaVu Sans'
plt.rcParams['font.size'] = 11
plt.rcParams['axes.titlesize'] = 14
plt.rcParams['axes.labelsize'] = 12

# Datos originales
months = ['Ene', 'Feb', 'Mar', 'Abr', 'May', 'Jun', 'Jul', 'Ago', 'Sep', 'Oct', 'Nov', 'Dic']
gold_usd = [2700, 2850, 2920, 2950, 3050, 3150, 3372, 3420, 3665, 4054, 4217, 4500]
silver_usd = [30.41, 32.15, 33.19, 29.58, 32.50, 33.80, 35.50, 38.20, 42.82, 49.44, 50.43, 62.34]
copper_usd = [13066.54, 12800, 12500, 12200, 11800, 11500, 11200, 10900, 10800, 11200, 10800, 12000]

# Normalizar a enero = 100
gold_norm = [(v / gold_usd[0]) * 100 for v in gold_usd]
silver_norm = [(v / silver_usd[0]) * 100 for v in silver_usd]
copper_norm = [(v / copper_usd[0]) * 100 for v in copper_usd]

# Crear figura con dos subgráficos
fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 10), height_ratios=[2, 1])

# --- Grafico 1: Precios originales con ejes secundarios ---
ax1_twin = ax1.twinx()

# Oro - eje izquierdo
line1, = ax1.plot(months, gold_usd, 'o-', color='#FFD700', linewidth=2.5, 
                  markersize=8, label='Oro (USD/onza)', markeredgecolor='#B8860B', markeredgewidth=1.5)
ax1.fill_between(months, gold_usd, alpha=0.15, color='#FFD700')
ax1.set_ylabel('Oro (USD/onza)', color='#B8860B', fontweight='bold')
ax1.tick_params(axis='y', labelcolor='#B8860B')
ax1.set_ylim(2000, 5000)

# Cobre - eje izquierdo (compartido con oro)
line3, = ax1.plot(months, copper_usd, 's-', color='#B87333', linewidth=2.5, 
                  markersize=8, label='Cobre (USD/ton)', markeredgecolor='#8B4513', markeredgewidth=1.5)
ax1.fill_between(months, copper_usd, alpha=0.1, color='#B87333')

# Plata - eje derecho
line2, = ax1_twin.plot(months, silver_usd, '^-', color='#C0C0C0', linewidth=2.5, 
                       markersize=8, label='Plata (USD/onza)', markeredgecolor='#696969', markeredgewidth=1.5)
ax1_twin.fill_between(months, silver_usd, alpha=0.15, color='#C0C0C0')
ax1_twin.set_ylabel('Plata (USD/onza)', color='#696969', fontweight='bold')
ax1_twin.tick_params(axis='y', labelcolor='#696969')
ax1_twin.set_ylim(25, 70)

ax1.set_title('Evolucion de Precios de Metales - 2025', fontsize=16, fontweight='bold', pad=15)
ax1.set_xlabel('')
lines = [line1, line2, line3]
labels = [l.get_label() for l in lines]
ax1.legend(lines, labels, loc='upper left', framealpha=0.95, fancybox=True)
ax1.grid(True, alpha=0.3)

# Anotaciones de picos
ax1.annotate(f'${gold_usd[-1]:,}', xy=(11, gold_usd[-1]), xytext=(10.2, gold_usd[-1]+200),
             fontsize=10, fontweight='bold', color='#B8860B',
             arrowprops=dict(arrowstyle='->', color='#B8860B', lw=1))
ax1_twin.annotate(f'${silver_usd[-1]:.2f}', xy=(11, silver_usd[-1]), xytext=(10.2, silver_usd[-1]+5),
                  fontsize=10, fontweight='bold', color='#696969',
                  arrowprops=dict(arrowstyle='->', color='#696969', lw=1))

# --- Grafico 2: Comparacion normalizada ---
colors = ['#FFD700', '#C0C0C0', '#B87333']
markers = ['o', '^', 's']

for i, (data, color, marker, name) in enumerate(zip(
    [gold_norm, silver_norm, copper_norm], 
    colors, markers, 
    ['Oro', 'Plata', 'Cobre'])):
    ax2.plot(months, data, f'{marker}-', color=color, linewidth=2.5, 
             markersize=8, label=f'{name} (base=Ene=100)', 
             markeredgecolor='white', markeredgewidth=1)
    ax2.fill_between(months, data, alpha=0.1, color=color)

ax2.axhline(y=100, color='gray', linestyle='--', linewidth=1, alpha=0.7, label='Base (Enero)')
ax2.set_ylabel('Indice (Enero 2025 = 100)', fontweight='bold')
ax2.set_xlabel('Mes (2025)', fontweight='bold')
ax2.set_title('Comparacion Normalizada - Eliminando Sesgo de Escala', fontsize=13, fontweight='bold', pad=10)
ax2.legend(loc='upper left', framealpha=0.95, fancybox=True)
ax2.grid(True, alpha=0.3)
ax2.set_ylim(70, 220)

# Anotaciones de variacion final
for i, (data, color, name) in enumerate(zip(
    [gold_norm, silver_norm, copper_norm],
    colors, ['Oro', 'Plata', 'Cobre'])):
    change = data[-1] - 100
    ax2.annotate(f'+{change:.0f}%', xy=(11, data[-1]), xytext=(11.2, data[-1]),
                 fontsize=10, fontweight='bold', color=color)

plt.tight_layout()
plt.savefig('workspace/charts/metales_evolucion_2025.png', dpi=150, bbox_inches='tight', 
            facecolor='white', edgecolor='none')
plt.close()

print("Grafico guardado: workspace/charts/metales_evolucion_2025.png")

# Imprimir resumen de datos normalizados
print("\n=== DATOS NORMALIZADOS (Enero 2025 = 100) ===")
print(f"\n{'Mes':<6} {'Oro':<10} {'Plata':<10} {'Cobre':<10}")
print("-" * 36)
for m, g, s, c in zip(months, gold_norm, silver_norm, copper_norm):
    print(f"{m:<6} {g:>7.1f}%   {s:>7.1f}%   {c:>7.1f}%")

print(f"\n--- Variacion Anual ---")
print(f"Oro:   +{gold_norm[-1]-100:.1f}% (de $2,700 a $4,500)")
print(f"Plata: +{silver_norm[-1]-100:.1f}% (de $30.41 a $62.34)")
print(f"Cobre: {copper_norm[-1]-100:+.1f}% (de ${copper_usd[0]:,.0f} a ${copper_usd[-1]:,.0f})")