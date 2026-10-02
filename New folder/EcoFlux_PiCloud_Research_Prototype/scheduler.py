from copy import deepcopy
from datetime import datetime
import hashlib
import math
import time

from config import ENERGY_THRESHOLD, LOW_UTIL_THRESHOLD, HIGH_UTIL_THRESHOLD, BASE_POWER, LOAD_POWER_FACTOR, NETWORK_OVERHEAD

class EcoFluxScheduler:
    """Software model of the EcoFlux PiCloud architecture.

    The model combines ideas from the supplied literature:
    - task + power-aware scheduling (EEH)
    - carbon-intensity-aware placement (Green Cloud framework)
    - workload/resource modeling and auto-scaling (SCORCH)
    - low-power Raspberry Pi distributed computing (TopADDPi)
    - optional renewable-energy availability (Green Video Transcoding / solar paper)
    - node consolidation / sleep states (Green IT / EEH)

    It does not claim physical Raspberry Pi measurements.
    """
    def __init__(self, nodes):
        self.initial_nodes = deepcopy(nodes)
        self.nodes = deepcopy(nodes)
        self.task_counter = 0
        self.events = []
        self.carbon_index = 180.0
        self.renewable_pct = 55.0

    def reset(self):
        self.nodes = deepcopy(self.initial_nodes)
        self.task_counter = 0
        self.events = []
        self.carbon_index = 180.0
        self.renewable_pct = 55.0

    def _update_energy_context(self):
        # Deterministic time-varying simulation so the demo is reproducible.
        self.carbon_index = round(120 + 90 * (0.5 + 0.5 * math.sin(self.task_counter / 2.0)), 2)
        self.renewable_pct = round(35 + 45 * (0.5 + 0.5 * math.cos(self.task_counter / 2.5)), 2)

    def _active_nodes(self):
        return [n for n in self.nodes if n['state'] == 'Active']

    def _wake_if_needed(self, workload):
        active = self._active_nodes()
        if not active or workload > 75:
            sleeping = [n for n in self.nodes if n['state'] == 'Sleep']
            if sleeping:
                node = max(sleeping, key=lambda n: n['energy'])
                node['state'] = 'Active'
                node['status'] = 'Woken for workload'
                self.events.append(f"{node['id']} woke due to workload demand")

    def _conventional_select(self):
        candidates = self._active_nodes() or self.nodes
        return min(candidates, key=lambda n: (n['utilization'], -n['energy']))

    def _ecoflux_score(self, node, priority, workload, deadline):
        headroom = max(0.0, 100.0 - node['utilization']) / 100.0
        energy = node['energy'] / 100.0
        carbon_goodness = 1.0 - min(1.0, self.carbon_index / 300.0)
        renewable = self.renewable_pct / 100.0
        workload_fit = max(0.0, 1.0 - workload / max(1, node['capacity']))
        urgency = {1: 1.0, 2: 0.65, 3: 0.35}[priority]
        deadline_factor = max(0.0, min(1.0, 1.0 - deadline / 30.0))
        # Balanced score: energy + carbon + capacity/headroom + task urgency.
        return (
            0.30 * energy +
            0.20 * carbon_goodness +
            0.20 * headroom +
            0.15 * workload_fit +
            0.10 * renewable +
            0.05 * (urgency + deadline_factor) / 2.0
        )

    def _energy_aware_select(self, priority, workload, deadline):
        candidates = [n for n in self._active_nodes() if n['energy'] >= ENERGY_THRESHOLD]
        if not candidates:
            candidates = self._active_nodes() or self.nodes
        return max(candidates, key=lambda n: self._ecoflux_score(n, priority, workload, deadline))

    def _consolidate(self):
        active = self._active_nodes()
        if len(active) <= 1:
            return
        # Put the least-used, lower-energy node to sleep only when another active node
        # has enough headroom. This mirrors the consolidation idea without migration.
        target = min(active, key=lambda n: (n['utilization'], n['energy']))
        busiest = max(active, key=lambda n: n['utilization'])
        if target['utilization'] < LOW_UTIL_THRESHOLD and busiest['utilization'] < HIGH_UTIL_THRESHOLD:
            target['state'] = 'Sleep'
            target['status'] = 'Consolidated / Sleep'
            self.events.append(f"{target['id']} consolidated to sleep state")

    def _model_cost(self, node, workload):
        load_ratio = workload / max(1, node['capacity'])
        energy_cost = BASE_POWER * 0.25 + LOAD_POWER_FACTOR * load_ratio + NETWORK_OVERHEAD
        energy_cost += 0.018 * node['utilization']
        return round(max(0.25, energy_cost), 3)

    def _model_time(self, node, workload, mode):
        load_ratio = workload / max(1, node['capacity'])
        scheduler_penalty = 0.08 if mode == 'energy_aware' else 0.0
        return round(0.55 + 1.35 * load_ratio + 0.012 * node['utilization'] + scheduler_penalty, 3)

    def execute(self, task_name, workload, priority, deadline, mode='energy_aware'):
        self.task_counter += 1
        self._update_energy_context()
        self._wake_if_needed(workload)
        if mode == 'conventional':
            node = self._conventional_select()
        else:
            node = self._energy_aware_select(priority, workload, deadline)

        before_energy = node['energy']
        before_util = node['utilization']
        model_energy_cost = self._model_cost(node, workload)
        model_time = self._model_time(node, workload, mode)
        carbon_cost = round(model_energy_cost * self.carbon_index / 1000.0, 4)
        new_util = min(96.0, before_util + 7.0 + 23.0 * workload / node['capacity'])

        # Small real CPU operation: proves that a software task was executed.
        start = time.perf_counter()
        digest = hashlib.sha256(f'{task_name}:{workload}:{priority}:{self.task_counter}'.encode()).hexdigest()
        for _ in range(max(800, workload * 250)):
            digest = hashlib.sha256(digest.encode()).hexdigest()
        observed_runtime = round(time.perf_counter() - start, 6)

        node['energy'] = round(max(5.0, before_energy - model_energy_cost), 2)
        node['utilization'] = round(new_util, 2)
        node['tasks'] += 1
        node['status'] = 'Completed'

        if mode == 'energy_aware':
            self._consolidate()

        return {
            'timestamp': datetime.now().isoformat(timespec='seconds'),
            'task_id': self.task_counter,
            'task_name': task_name,
            'workload': workload,
            'priority': priority,
            'deadline_s': deadline,
            'mode': 'EcoFlux PiCloud' if mode == 'energy_aware' else 'Conventional Scheduling',
            'node': node['id'],
            'energy_before_model': before_energy,
            'energy_model_cost': model_energy_cost,
            'energy_after_model': node['energy'],
            'carbon_index_gco2_kwh_model': self.carbon_index,
            'renewable_availability_pct_model': self.renewable_pct,
            'carbon_impact_model': carbon_cost,
            'model_execution_time_s': model_time,
            'observed_python_runtime_s': observed_runtime,
            'node_utilization_pct': node['utilization'],
            'node_state': node['state'],
            'status': 'Completed',
            'result_hash': digest[:16],
        }
