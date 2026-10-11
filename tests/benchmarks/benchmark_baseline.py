"""Reproducible local benchmark baseline for Neatify's current engine.

This script intentionally creates temporary files only. It never touches the
user's real Desktop, Downloads, Documents, or external drives.
"""

import json
import os
import platform
import shutil
import sys
import tempfile
import time
import tracemalloc
from contextlib import redirect_stdout
from datetime import datetime
from io import StringIO


PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
BENCHMARK_DATA_DIR = tempfile.mkdtemp(prefix="neatify_benchmark_app_data_")
os.environ.setdefault("NEATIFY_DATA_DIR", BENCHMARK_DATA_DIR)

if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

import neatify  # noqa: E402
from rules import get_arrangement_for_file_with_rules, load_rules  # noqa: E402


DATASET_SIZES = [100, 1000, 10000]
EXTENSIONS = ["pdf", "jpg", "mp4", "zip", "xlsx", "txt", "py", "custom"]


def create_dataset(root, entry_count):
    for index in range(entry_count):
        extension = EXTENSIONS[index % len(EXTENSIONS)]
        file_path = os.path.join(root, "file_" + str(index).zfill(7) + "." + extension)

        with open(file_path, "w", encoding="utf-8") as benchmark_file:
            benchmark_file.write("x")


def measure_peak_memory(function):
    tracemalloc.start()
    started = time.perf_counter()
    result = function()
    elapsed = time.perf_counter() - started
    current_memory, peak_memory = tracemalloc.get_traced_memory()
    tracemalloc.stop()

    return result, elapsed, peak_memory


def scan_folder(folder):
    count = 0

    with os.scandir(folder) as entries:
        for entry in entries:
            try:
                if entry.is_file(follow_symlinks=False):
                    count = count + 1
            except OSError:
                pass

    return count


def plan_folder(folder):
    rules = load_rules()
    moves = []
    taken_names_by_folder = {}

    with os.scandir(folder) as entries:
        for entry in entries:
            try:
                if not entry.is_file(follow_symlinks=False):
                    continue
            except OSError:
                continue

            arrangement = get_arrangement_for_file_with_rules(entry.name, folder, rules)
            destination_folder = os.path.join(folder, arrangement["destination"])
            destination = os.path.join(destination_folder, entry.name)
            unique_destination = neatify.get_unique_destination_with_name_cache(destination, taken_names_by_folder)
            moves.append((entry.path, unique_destination))

    return moves


def execute_plan(moves):
    moved_count = 0

    for old_path, new_path in moves:
        os.makedirs(os.path.dirname(new_path), exist_ok=True)
        os.rename(old_path, new_path)
        moved_count = moved_count + 1

    return moved_count


def execute_plan_with_journal(moves):
    moved_count = 0

    for old_path, new_path in moves:
        os.makedirs(os.path.dirname(new_path), exist_ok=True)

        with redirect_stdout(StringIO()):
            neatify.move_file(old_path, new_path, dry_run=False, move_id="benchmark_batch")

        moved_count = moved_count + 1

    return moved_count


def benchmark_size(entry_count):
    root = tempfile.mkdtemp(prefix="neatify_benchmark_")
    journal_root = tempfile.mkdtemp(prefix="neatify_benchmark_journal_")

    try:
        create_dataset(root, entry_count)
        create_dataset(journal_root, entry_count)

        scan_count, scan_time, scan_peak = measure_peak_memory(lambda: scan_folder(root))
        moves, planning_time, planning_peak = measure_peak_memory(lambda: plan_folder(root))
        journal_moves, journal_planning_time, journal_planning_peak = measure_peak_memory(lambda: plan_folder(journal_root))
        moved_count, execution_time, execution_peak = measure_peak_memory(lambda: execute_plan(moves))
        journal_moved_count, journal_execution_time, journal_execution_peak = measure_peak_memory(lambda: execute_plan_with_journal(journal_moves))

        return {
            "entries": entry_count,
            "scan_count": scan_count,
            "planned_moves": len(moves),
            "moved_count": moved_count,
            "journal_planned_moves": len(journal_moves),
            "journal_moved_count": journal_moved_count,
            "scan_seconds": scan_time,
            "planning_seconds": planning_time,
            "execution_seconds": execution_time,
            "journal_planning_seconds": journal_planning_time,
            "journal_execution_seconds": journal_execution_time,
            "scan_peak_bytes": scan_peak,
            "planning_peak_bytes": planning_peak,
            "execution_peak_bytes": execution_peak,
            "journal_planning_peak_bytes": journal_planning_peak,
            "journal_execution_peak_bytes": journal_execution_peak,
        }
    finally:
        shutil.rmtree(root, ignore_errors=True)
        shutil.rmtree(journal_root, ignore_errors=True)


def main():
    results = {
        "created_at": datetime.now().isoformat(timespec="seconds"),
        "python": sys.version,
        "platform": platform.platform(),
        "processor": platform.processor(),
        "machine": platform.machine(),
        "dataset_note": "Temporary flat directories with small text files and mixed extensions. Raw execution uses os.rename directly; journal execution uses neatify.move_file with JSONL fsync.",
        "results": [],
    }

    for entry_count in DATASET_SIZES:
        results["results"].append(benchmark_size(entry_count))

    output_folder = os.path.join(PROJECT_ROOT, "tests", "benchmarks", "results")
    output_path = os.path.join(output_folder, "baseline_local.json")

    try:
        os.makedirs(output_folder, exist_ok=True)

        with open(output_path, "w", encoding="utf-8") as output_file:
            json.dump(results, output_file, indent=4)
    except OSError:
        output_path = os.path.join(tempfile.gettempdir(), "neatify_baseline_local.json")

        with open(output_path, "w", encoding="utf-8") as output_file:
            json.dump(results, output_file, indent=4)

    print(json.dumps(results, indent=4))
    print("Wrote", output_path)
    shutil.rmtree(BENCHMARK_DATA_DIR, ignore_errors=True)


if __name__ == "__main__":
    main()
