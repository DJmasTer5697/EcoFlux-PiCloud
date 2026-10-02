from scheduler import EcoFluxScheduler
from storage import save_run
from config import NODES

TASKS = [
    ('Pi Calculation', 35, 2, 12),
    ('Matrix Processing', 60, 1, 8),
    ('Data Aggregation', 45, 3, 20),
    ('Image Batch', 80, 1, 6),
    ('Analytics Job', 55, 2, 10),
    ('Report Generation', 30, 3, 25),
]

def run_mode(mode):
    s = EcoFluxScheduler(NODES)
    results = []
    for name, workload, priority, deadline in TASKS:
        result = s.execute(name, workload, priority, deadline, mode)
        save_run(result)
        results.append(result)
    return results

if __name__ == '__main__':
    for mode in ('conventional', 'energy_aware'):
        results = run_mode(mode)
        total = sum(r['energy_model_cost'] for r in results)
        avg_time = sum(r['model_execution_time_s'] for r in results) / len(results)
        avg_carbon = sum(r['carbon_impact_model'] for r in results)
        print(f'\n{mode}: energy_model={total:.3f}, avg_time={avg_time:.3f}s, carbon_impact_model={avg_carbon:.4f}')
    print('\nDemo complete. See results/task_history.csv')
