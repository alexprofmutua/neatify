# Neatify Operation Journal

Neatify uses SQLite as the source of truth for move history, undo status, and high-volume batch arrange operations. The JSONL journal remains a crash-recovery safety log.

## Why SQLite

SQLite gives Neatify durable local transactions, fast history queries, and much better throughput for large arrange batches. Settings and user rules remain JSON because they are small preference files.

## SQLite Records

SQLite stores:

- `batches`: one arrange batch, its action, status, and timestamps.
- `operations`: one planned file move with operation ID, batch ID, old path, new path, state, and error information.
- `legacy_imports`: a marker that an old text-history file has already been imported.

The JSONL journal still exists for crash recovery and compatibility with older interrupted operations. Malformed or truncated JSONL records are ignored safely during reads and surfaced as `malformed_record` entries.

## Legacy History Import

Older versions of Neatify wrote move history to `neatify_history.txt`. Current History reads from SQLite only.

On first History read, Neatify imports valid text-history records into SQLite and records the source file in `legacy_imports`. The old text file remains on disk as a backup, but it is not used as a live History source after import.

## Operation States

Move states:

- `planned`
- `moving`
- `moved`
- `history_committed`
- `failed`
- `recovered_no_move`
- `recovery_conflict`

Undo states:

- `undo_planned`
- `undo_moving`
- `undo_moved`
- `undo_history_committed`
- `undo_failed`

A `moving` record does not prove that a rename completed. Recovery reconciles journal state with actual source and destination paths.

## Durability Ordering

Before a filesystem mutation, Neatify appends intent to the journal, flushes Python buffers, and calls `fsync()` on the journal file.

On POSIX systems, when a journal file or lock file is newly created, Neatify also attempts to `fsync()` the parent directory. Windows directory synchronization is platform-dependent and currently treated as a limitation.

The single-file CLI order is:

```text
SQLite plan transaction
planned -> fsync
moving -> fsync
rename
moved -> fsync
SQLite result transaction
history_committed -> fsync
```

This favors crash recovery over throughput.

The GUI arrange flow uses a faster SQLite batch-safe order:

```text
SQLite batch plan transaction
rename files
SQLite batch result transaction
```

The batch path still records intent before any file moves. If Neatify stops halfway through the rename loop, recovery compares each planned source and destination path with the real filesystem and marks completed moves safely.

## Recovery

Recovery is idempotent. Running recovery multiple times should not duplicate moves, overwrite files, or corrupt history.

SQLite-owned operations are recovered through SQLite. JSONL recovery is used only for older operations that do not exist in SQLite, which prevents the same interrupted move from being counted twice.

Recovery checks the real filesystem:

- Source exists, destination missing: no move completed.
- Source missing, destination exists: move likely completed; commit missing history.
- Both exist or both missing: record a recovery conflict.

Neatify never overwrites an existing file during recovery or undo.

## Security Notes

Neatify avoids following symlink files during arrange scans and checks destination paths with `realpath()` and `commonpath()`.

Remaining platform-dependent concerns:

- Junctions and reparse points on Windows need deeper platform-specific tests.
- A path can change between validation and rename, so TOCTOU risk is reduced but not fully eliminated.
- Unix `os.rename()` can overwrite if a destination appears after validation. Neatify checks before moving, but a fully race-proof no-overwrite rename requires platform-specific primitives or a different move strategy.

## Performance Trade-off

The single-file path still writes durable JSONL recovery states and now records history in SQLite. The GUI arrange path uses SQLite transactions so large arrange operations avoid thousands of repeated file locks and `fsync()` calls while preserving write-ahead intent and undo history.
