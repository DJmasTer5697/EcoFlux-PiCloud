from pathlib import Path
import shutil
import subprocess
import sys

ROOT = Path(__file__).resolve().parent
csv_file = ROOT / "results" / "task_history.csv"
backup = ROOT / "results" / "task_history_backup.csv"

if csv_file.exists():
    shutil.copy2(csv_file, backup)
    csv_file.unlink()

print("Old task history backed up to results/task_history_backup.csv")
print("Running clean controlled experiment...")
subprocess.run([sys.executable, "run_demo.py"], cwd=ROOT, check=True)
subprocess.run([sys.executable, "generate_figures.py"], cwd=ROOT, check=True)
print("Done. Clean 12-observation dataset generated.")
