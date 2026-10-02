from pathlib import Path
import csv

RESULTS = Path('results')
RESULTS.mkdir(exist_ok=True)
HISTORY = RESULTS / 'task_history.csv'
FIELDS = [
    'timestamp','task_id','task_name','workload','priority','deadline_s','mode','node',
    'energy_before_model','energy_model_cost','energy_after_model',
    'carbon_index_gco2_kwh_model','renewable_availability_pct_model','carbon_impact_model',
    'model_execution_time_s','observed_python_runtime_s','node_utilization_pct','node_state','status','result_hash'
]

def save_run(result):
    exists = HISTORY.exists()
    with HISTORY.open('a', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=FIELDS)
        if not exists:
            writer.writeheader()
        writer.writerow({k: result.get(k, '') for k in FIELDS})

def load_history(limit=50):
    if not HISTORY.exists():
        return []
    with HISTORY.open(newline='', encoding='utf-8') as f:
        rows = list(csv.DictReader(f))
    return rows[-limit:][::-1]
