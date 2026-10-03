from flask import Flask, render_template, request, redirect, url_for, jsonify, send_file
from scheduler import EcoFluxScheduler
from storage import save_run, load_history, HISTORY
from config import NODES, PROJECT_TITLE

app = Flask(__name__)
scheduler = EcoFluxScheduler(NODES)

@app.route('/')
def index():
    return render_template('index.html', title=PROJECT_TITLE, nodes=scheduler.nodes, history=load_history(), carbon=scheduler.carbon_index, renewable=scheduler.renewable_pct, events=scheduler.events[-8:])

@app.post('/run')
def run_task():
    try:
        task_name = request.form.get('task_name', 'Eco Task').strip() or 'Eco Task'
        workload = int(request.form.get('workload', 50))
        priority = int(request.form.get('priority', 2))
        deadline = float(request.form.get('deadline', 10))
        mode = request.form.get('mode', 'energy_aware')
        if not 1 <= workload <= 100 or priority not in (1, 2, 3) or not 1 <= deadline <= 60 or mode not in ('energy_aware','conventional'):
            raise ValueError
        result = scheduler.execute(task_name, workload, priority, deadline, mode)
        save_run(result)
    except (ValueError, TypeError):
        pass
    return redirect(url_for('index'))

@app.post('/reset')
def reset():
    scheduler.reset()
    return redirect(url_for('index'))

@app.get('/api/status')
def status():
    return jsonify({'nodes': scheduler.nodes, 'history': load_history(), 'carbon_index': scheduler.carbon_index, 'renewable_pct': scheduler.renewable_pct, 'events': scheduler.events[-8:]})

@app.get('/download-history')
def download_history():
    # Download the complete CSV used by the scheduler history.
    if not HISTORY.exists():
        return jsonify({'error': 'No task history has been recorded yet.'}), 404
    return send_file(
        HISTORY,
        mimetype='text/csv',
        as_attachment=True,
        download_name='task_history.csv'
    )

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5000, debug=False)
