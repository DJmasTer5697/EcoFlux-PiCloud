from pathlib import Path
import csv
from collections import defaultdict
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parent
CSV_FILE = ROOT / 'results' / 'task_history.csv'
OUT = ROOT / 'figures'
OUT.mkdir(exist_ok=True)

rows = []
with CSV_FILE.open(newline='', encoding='utf-8') as f:
    rows = list(csv.DictReader(f))

# Keep latest occurrence for each task+mode.
latest = {}
for r in rows:
    latest[(r['task_name'], r['mode'])] = r

names = []
for r in latest.values():
    if r['task_name'] not in names:
        names.append(r['task_name'])

modes = ['Conventional Scheduling', 'EcoFlux PiCloud']

def values(field):
    out = []
    for mode in modes:
        out.append([float(latest[(n, mode)][field]) if (n, mode) in latest else 0 for n in names])
    return out

# Fig. 3 — model energy comparison
vals = values('energy_model_cost')
x = range(len(names))
width = 0.36
plt.figure(figsize=(10, 5.5), dpi=400)
plt.bar([i-width/2 for i in x], vals[0], width, label=modes[0])
plt.bar([i+width/2 for i in x], vals[1], width, label=modes[1])
plt.xticks(list(x), names, rotation=30, ha='right')
plt.ylabel('Model energy cost (arbitrary units)')
plt.title('Energy Cost Comparison')
plt.legend()
plt.tight_layout()
plt.savefig(OUT / 'fig3_energy_comparison.png', bbox_inches='tight')
plt.close()

# Fig. 4 — modeled execution time
vals = values('model_execution_time_s')
plt.figure(figsize=(10, 5.5), dpi=400)
plt.bar([i-width/2 for i in x], vals[0], width, label=modes[0])
plt.bar([i+width/2 for i in x], vals[1], width, label=modes[1])
plt.xticks(list(x), names, rotation=30, ha='right')
plt.ylabel('Modeled execution time (s)')
plt.title('Execution Time Comparison')
plt.legend()
plt.tight_layout()
plt.savefig(OUT / 'fig4_execution_time.png', bbox_inches='tight')
plt.close()

# Fig. 5 — modeled carbon impact
vals = values('carbon_impact_model')
plt.figure(figsize=(10, 5.5), dpi=400)
plt.bar([i-width/2 for i in x], vals[0], width, label=modes[0])
plt.bar([i+width/2 for i in x], vals[1], width, label=modes[1])
plt.xticks(list(x), names, rotation=30, ha='right')
plt.ylabel('Modeled carbon impact (relative units)')
plt.title('Carbon-Impact Comparison')
plt.legend()
plt.tight_layout()
plt.savefig(OUT / 'fig5_carbon_impact.png', bbox_inches='tight')
plt.close()

print('Figures generated in', OUT)
