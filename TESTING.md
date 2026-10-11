# Testing Neatify

Neatify's safety tests use `pytest` and temporary directories. They must never run against a user's real Desktop, Downloads, Documents, or external drives.

## Install Test Tools

macOS/Linux:

```bash
cd /Users/alexprof/Projects/_active/neatify
source neat/bin/activate
python -m pip install -r requirements-dev.txt
```

Windows PowerShell:

```powershell
cd C:\path\to\neatify
.\neat\Scripts\Activate.ps1
python -m pip install -r requirements-dev.txt
```

## Run Tests

macOS/Linux:

```bash
python -m pytest
```

Windows:

```powershell
python -m pytest
```

Known production defects are marked with `xfail`. These are expected failures that document current safety gaps, not passing behavior.

## Run Benchmarks

The baseline benchmark creates temporary files for 100, 1,000, and 10,000 entries, then measures scan time, planning time, execution time, and peak memory using `tracemalloc`.

```bash
python tests/benchmarks/benchmark_baseline.py
```

Results are written to:

```text
tests/benchmarks/results/baseline_local.json
```

Benchmark numbers depend on hardware, operating system, filesystem, current machine load, and whether the filesystem cache is warm or cold. Treat them as local baselines, not universal product claims.

The Phase 2 benchmark compares raw `os.rename` execution with journaled `neatify.move_file` execution. Journaled execution is expected to be slower because it performs durable JSONL writes and `fsync()` calls around each filesystem mutation.
