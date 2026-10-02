PROJECT_TITLE = 'EcoFlux PiCloud'
ENERGY_THRESHOLD = 35.0
LOW_UTIL_THRESHOLD = 22.0
HIGH_UTIL_THRESHOLD = 78.0
MAX_NODES = 4

NODES = [
    {'id': 'Pi-01', 'capacity': 100, 'energy': 92.0, 'utilization': 18.0, 'tasks': 0, 'state': 'Active'},
    {'id': 'Pi-02', 'capacity': 95,  'energy': 78.0, 'utilization': 25.0, 'tasks': 0, 'state': 'Active'},
    {'id': 'Pi-03', 'capacity': 90,  'energy': 61.0, 'utilization': 32.0, 'tasks': 0, 'state': 'Active'},
    {'id': 'Pi-04', 'capacity': 85,  'energy': 44.0, 'utilization': 40.0, 'tasks': 0, 'state': 'Active'},
]

# Software-model values inspired by the literature. They are NOT measured hardware watts/Wh.
BASE_POWER = 1.8
LOAD_POWER_FACTOR = 2.6
NETWORK_OVERHEAD = 0.12
