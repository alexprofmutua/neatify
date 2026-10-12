"""Measure Neatify speed on the current computer.

This benchmark creates temporary files only. It does not touch Downloads,
Desktop, Documents, or external drives.
"""

import json
import os
import platform
import shutil
import sys
import tempfile
import time
import tracemalloc
from datetime import datetime


PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
APP_DATA_DIR = tempfile.mkdtemp(prefix="neatify_speed_app_data_")
os.environ["NEATIFY_DATA_DIR"] = APP_DATA_DIR

if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

import neatify  # noqa: E402
from rules import find_with_filters, get_arrangement_for_file_with_rules, load_rules  # noqa: E402


DATASET_SIZES = [100, 1000, 10000]
EXTENSIONS = ["pdf", "jpg", "png", "mp4", "zip", "xlsx", "txt", "py", "json", "custom"]


def create_dataset(folder, entry_count):
    os.makedirs(folder, exist_ok=True)

    for index in range(entry_count):
        extension = EXTENSIONS[index % len(EXTENSIONS)]
        file_name = "file_" + str(index).zfill(7) + "." + extension
        file_path = os.path.join(folder, file_name)

        with open(file_path, "w", encoding="utf-8") as test_file:
            test_file.write("x")


def measure(function):
    tracemalloc.start()
    started = time.perf_counter()
    result = function()
    elapsed = time.perf_counter() - started
    current_memory, peak_memory = tracemalloc.get_traced_memory()
    tracemalloc.stop()

    return result, elapsed, peak_memory


def scan_folder(folder):
    folder_count = 0
    file_count = 0

    with os.scandir(folder) as entries:
        for entry in entries:
            try:
                if entry.is_dir(follow_symlinks=False):
                    folder_count = folder_count + 1
                elif entry.is_file(follow_symlinks=False):
                    file_count = file_count + 1
            except OSError:
                pass

    return {
        "folders": folder_count,
        "files": file_count,
    }


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

            moves.append({
                "old_path": entry.path,
                "new_path": unique_destination,
            })

    return moves


def benchmark_size(entry_count):
    root = tempfile.mkdtemp(prefix="neatify_speed_")

    try:
        create_dataset(root, entry_count)

        scan_result, scan_seconds, scan_peak_bytes = measure(lambda: scan_folder(root))
        move_plan, planning_seconds, planning_peak_bytes = measure(lambda: plan_folder(root))
        arrange_result, execution_seconds, execution_peak_bytes = measure(
            lambda: neatify.move_files_batch(move_plan, move_id="benchmark_" + str(entry_count))
        )

        search_text = "file_000"
        find_result, find_seconds, find_peak_bytes = measure(
            lambda: find_with_filters(search_text, root, search_type="Files", include_subfolders=True)
        )

        return {
            "entries": entry_count,
            "scan_result": scan_result,
            "planned_moves": len(move_plan),
            "moved_count": arrange_result["moved_count"],
            "arrange_errors": len(arrange_result["errors"]),
            "find_matches": len(find_result),
            "scan_seconds": scan_seconds,
            "planning_seconds": planning_seconds,
            "execution_seconds": execution_seconds,
            "total_arrange_seconds": planning_seconds + execution_seconds,
            "find_seconds": find_seconds,
            "scan_peak_bytes": scan_peak_bytes,
            "planning_peak_bytes": planning_peak_bytes,
            "execution_peak_bytes": execution_peak_bytes,
            "find_peak_bytes": find_peak_bytes,
        }
    finally:
        shutil.rmtree(root, ignore_errors=True)


def main():
    try:
        results = {
            "created_at": datetime.now().isoformat(timespec="seconds"),
            "python": sys.version,
            "platform": platform.platform(),
            "processor": platform.processor(),
            "machine": platform.machine(),
            "dataset_note": "Temporary flat folders with tiny files. Arrange uses the same SQLite batch path as the GUI.",
            "results": [],
        }

        for entry_count in DATASET_SIZES:
            results["results"].append(benchmark_size(entry_count))

        output_name = "speed_" + platform.system().lower() + ".json"

        try:
            output_folder = os.path.join(PROJECT_ROOT, "tests", "benchmarks", "results")
            os.makedirs(output_folder, exist_ok=True)
            output_path = os.path.join(output_folder, output_name)

            with open(output_path, "w", encoding="utf-8") as output_file:
                json.dump(results, output_file, indent=4)
        except OSError:
            output_path = os.path.join(tempfile.gettempdir(), output_name)

            with open(output_path, "w", encoding="utf-8") as output_file:
                json.dump(results, output_file, indent=4)

        print(json.dumps(results, indent=4))
        print("Wrote", output_path)
    finally:
        shutil.rmtree(APP_DATA_DIR, ignore_errors=True)


if __name__ == "__main__":
    main()
