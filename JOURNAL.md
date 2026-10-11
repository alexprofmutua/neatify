# Neatify Operation Journal

Neatify uses a versioned JSONL write-ahead journal for filesystem mutations.

## Why JSONL

JSONL is append-only, human-readable, easy to test, and simple enough for the current local desktop app. SQLite would provide stronger built-in transactions and locking, but it adds more design surface area. Neatify can move to SQLite later if enterprise features, indexing, or higher write throughput require it.

## Journal Records

Each journal line is one JSON object with:

- `journal_version`
- `timestamp`
- `operation_id`
- `batch_id`
- `source_path`
- `destination_path`
- `state`
- source and destination metadata

Malformed or truncated records are ignored safely during reads and surfaced as `malformed_record` entries.

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

The basic order is:

```text
planned -> fsync
moving -> fsync
rename
moved -> fsync
history write -> fsync
history_committed -> fsync
```

This favors crash recovery over throughput.

## Recovery

Recovery is idempotent. Running recovery multiple times should not duplicate moves, overwrite files, or corrupt history.

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

The current journal writes several durable records per move. This is intentionally conservative and measurably slower than raw rename. Future optimization may batch some safe journal writes, but only after preserving crash-consistency guarantees.
