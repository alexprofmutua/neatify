"""SQLite storage for Neatify operation history and recovery."""

import hashlib
import os
import sqlite3
from datetime import datetime

from app_paths import get_user_data_path


SCHEMA_VERSION = 1


def get_database_path():
    return get_user_data_path("neatify.db")


def timestamp_now():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def connect_database():
    database_path = get_database_path()
    os.makedirs(os.path.dirname(database_path), exist_ok=True)
    connection = sqlite3.connect(database_path)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA journal_mode=WAL")
    connection.execute("PRAGMA synchronous=FULL")
    connection.execute("PRAGMA foreign_keys=ON")
    connection.execute("PRAGMA busy_timeout=5000")
    initialize_database(connection)
    return connection


def initialize_database(connection):
    connection.execute(
        """
        CREATE TABLE IF NOT EXISTS schema_info (
            version INTEGER PRIMARY KEY,
            applied_at TEXT NOT NULL
        )
        """
    )
    connection.execute(
        """
        CREATE TABLE IF NOT EXISTS batches (
            batch_id TEXT PRIMARY KEY,
            action TEXT NOT NULL,
            status TEXT NOT NULL,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL
        )
        """
    )
    connection.execute(
        """
        CREATE TABLE IF NOT EXISTS operations (
            operation_id TEXT PRIMARY KEY,
            batch_id TEXT NOT NULL,
            action TEXT NOT NULL,
            old_path TEXT NOT NULL,
            new_path TEXT NOT NULL,
            state TEXT NOT NULL,
            error_message TEXT,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL,
            FOREIGN KEY (batch_id) REFERENCES batches(batch_id)
        )
        """
    )
    connection.execute(
        """
        CREATE TABLE IF NOT EXISTS legacy_imports (
            source_path TEXT PRIMARY KEY,
            imported_at TEXT NOT NULL,
            imported_count INTEGER NOT NULL
        )
        """
    )
    connection.execute("CREATE INDEX IF NOT EXISTS idx_operations_batch ON operations(batch_id)")
    connection.execute("CREATE INDEX IF NOT EXISTS idx_operations_state ON operations(state)")
    connection.execute("CREATE INDEX IF NOT EXISTS idx_operations_paths ON operations(old_path, new_path)")
    connection.execute(
        "INSERT OR IGNORE INTO schema_info (version, applied_at) VALUES (?, ?)",
        (SCHEMA_VERSION, timestamp_now()),
    )
    connection.commit()


def record_batch_plan(batch_id, prepared_moves):
    if len(prepared_moves) == 0:
        return

    now = timestamp_now()

    with connect_database() as connection:
        connection.execute("BEGIN IMMEDIATE")
        connection.execute(
            """
            INSERT OR REPLACE INTO batches (batch_id, action, status, created_at, updated_at)
            VALUES (?, ?, ?, COALESCE((SELECT created_at FROM batches WHERE batch_id = ?), ?), ?)
            """,
            (batch_id, "move", "planned", batch_id, now, now),
        )
        connection.executemany(
            """
            INSERT OR REPLACE INTO operations
            (operation_id, batch_id, action, old_path, new_path, state, error_message, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            [
                (
                    move["operation_id"],
                    batch_id,
                    "move",
                    move["old_path"],
                    move["new_path"],
                    "planned",
                    None,
                    now,
                    now,
                )
                for move in prepared_moves
            ],
        )
        connection.commit()


def record_batch_results(batch_id, moved_moves, failed_moves):
    now = timestamp_now()

    with connect_database() as connection:
        connection.execute("BEGIN IMMEDIATE")
        connection.executemany(
            """
            UPDATE operations
            SET state = ?, error_message = NULL, updated_at = ?
            WHERE operation_id = ?
            """,
            [("moved", now, move["operation_id"]) for move in moved_moves],
        )
        connection.executemany(
            """
            UPDATE operations
            SET state = ?, error_message = ?, updated_at = ?
            WHERE operation_id = ?
            """,
            [("failed", move["error"], now, move["operation_id"]) for move in failed_moves],
        )
        batch_status = "history_committed"

        if len(failed_moves) > 0:
            batch_status = "completed_with_errors"

        connection.execute(
            "UPDATE batches SET status = ?, updated_at = ? WHERE batch_id = ?",
            (batch_status, now, batch_id),
        )
        connection.commit()


def read_sqlite_history_items():
    if not os.path.exists(get_database_path()):
        return []

    with connect_database() as connection:
        rows = connection.execute(
            """
            SELECT b.created_at, o.batch_id, o.action, o.old_path, o.new_path
            FROM operations o
            JOIN batches b ON b.batch_id = o.batch_id
            WHERE o.action = 'move' AND o.state = 'moved'
            ORDER BY b.created_at, o.rowid
            """
        ).fetchall()
        undone_rows = connection.execute(
            """
            SELECT b.updated_at, o.batch_id, o.old_path, o.new_path
            FROM operations o
            JOIN batches b ON b.batch_id = o.batch_id
            WHERE o.action = 'move'
              AND o.state = 'moved'
              AND b.status = 'undone'
            GROUP BY o.batch_id
            ORDER BY b.updated_at, o.rowid
            """
        ).fetchall()

    history_items = []

    for row in rows:
        history_items.append({
            "time": row["created_at"],
            "move_id": row["batch_id"],
            "action": "Moved",
            "item": os.path.basename(row["old_path"]),
            "from": os.path.dirname(row["old_path"]),
            "to": os.path.dirname(row["new_path"]),
            "path_for_icon": row["new_path"],
            "old_path": row["old_path"],
            "new_path": row["new_path"],
        })

    for row in undone_rows:
        history_items.append({
            "time": row["updated_at"],
            "move_id": row["batch_id"],
            "action": "UNDONE",
            "item": os.path.basename(row["new_path"]),
            "from": os.path.dirname(row["new_path"]),
            "to": os.path.dirname(row["old_path"]),
            "path_for_icon": row["old_path"],
            "old_path": row["new_path"],
            "new_path": row["old_path"],
        })

    return history_items


def import_legacy_history_items(source_path, history_items):
    if source_path == "" or len(history_items) == 0:
        return 0

    now = timestamp_now()
    imported_count = 0

    with connect_database() as connection:
        existing_import = connection.execute(
            "SELECT source_path FROM legacy_imports WHERE source_path = ?",
            (source_path,),
        ).fetchone()

        if existing_import is not None:
            return 0

        connection.execute("BEGIN IMMEDIATE")

        for history_item in history_items:
            move_id = history_item.get("move_id", "")
            action = history_item.get("action", "")
            old_path = history_item.get("old_path", "")
            new_path = history_item.get("new_path", "")
            created_at = history_item.get("time", now)

            if move_id == "" or old_path == "" or new_path == "":
                continue

            if action == "Moved":
                operation_id = create_legacy_operation_id(move_id, old_path, new_path)
                connection.execute(
                    """
                    INSERT OR IGNORE INTO batches (batch_id, action, status, created_at, updated_at)
                    VALUES (?, ?, ?, ?, ?)
                    """,
                    (move_id, "move", "history_committed", created_at, created_at),
                )
                connection.execute(
                    """
                    INSERT OR IGNORE INTO operations
                    (operation_id, batch_id, action, old_path, new_path, state, error_message, created_at, updated_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (operation_id, move_id, "move", old_path, new_path, "moved", None, created_at, created_at),
                )
                imported_count = imported_count + 1
            elif action == "UNDONE":
                connection.execute(
                    """
                    UPDATE batches
                    SET status = ?, updated_at = ?
                    WHERE batch_id = ?
                    """,
                    ("undone", created_at, move_id),
                )

        connection.execute(
            "INSERT INTO legacy_imports (source_path, imported_at, imported_count) VALUES (?, ?, ?)",
            (source_path, now, imported_count),
        )
        connection.commit()

    return imported_count


def create_legacy_operation_id(move_id, old_path, new_path):
    raw_value = move_id + "\0" + old_path + "\0" + new_path
    digest = hashlib.sha256(raw_value.encode("utf-8")).hexdigest()
    return "legacy_" + digest


def mark_batch_undone(batch_id):
    now = timestamp_now()

    with connect_database() as connection:
        connection.execute("BEGIN IMMEDIATE")
        connection.execute(
            "UPDATE batches SET status = ?, updated_at = ? WHERE batch_id = ?",
            ("undone", now, batch_id),
        )
        connection.commit()


def get_sqlite_operation_ids():
    if not os.path.exists(get_database_path()):
        return set()

    with connect_database() as connection:
        rows = connection.execute("SELECT operation_id FROM operations").fetchall()

    return {row["operation_id"] for row in rows}


def recover_sqlite_operations():
    if not os.path.exists(get_database_path()):
        return {"recovered": 0, "conflicts": 0}

    recovered_count = 0
    conflict_count = 0
    now = timestamp_now()

    with connect_database() as connection:
        rows = connection.execute(
            """
            SELECT operation_id, batch_id, old_path, new_path, state
            FROM operations
            WHERE state = 'planned'
            """
        ).fetchall()

        updates = []

        for row in rows:
            old_exists = os.path.exists(row["old_path"])
            new_exists = os.path.exists(row["new_path"])

            if new_exists and not old_exists:
                updates.append(("moved", None, now, row["operation_id"]))
                recovered_count = recovered_count + 1
            elif old_exists and not new_exists:
                updates.append(("recovered_no_move", None, now, row["operation_id"]))
            else:
                updates.append(("recovery_conflict", "Could not determine move result", now, row["operation_id"]))
                conflict_count = conflict_count + 1

        if len(updates) > 0:
            connection.execute("BEGIN IMMEDIATE")
            connection.executemany(
                """
                UPDATE operations
                SET state = ?, error_message = ?, updated_at = ?
                WHERE operation_id = ?
                """,
                updates,
            )
            connection.execute(
                """
                UPDATE batches
                SET status = 'recovered', updated_at = ?
                WHERE batch_id IN (
                    SELECT DISTINCT batch_id FROM operations
                    WHERE state IN ('moved', 'recovered_no_move', 'recovery_conflict')
                )
                """,
                (now,),
            )
            connection.commit()

    return {"recovered": recovered_count, "conflicts": conflict_count}
