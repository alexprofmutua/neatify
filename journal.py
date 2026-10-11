"""Durable JSONL operation journal for Neatify filesystem changes."""

import json
import os
import time
from datetime import datetime

from app_paths import get_user_data_path


JOURNAL_VERSION = 1
LOCK_TIMEOUT_SECONDS = 10


def get_journal_path():
    return get_user_data_path("neatify_journal.jsonl")


def create_operation_id():
    return "op_" + datetime.now().strftime("%Y%m%d%H%M%S%f")


def timestamp_now():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def get_path_metadata(item_path):
    try:
        stat_result = os.stat(item_path, follow_symlinks=False)
    except OSError:
        return {
            "exists": False,
            "size": None,
            "mtime_ns": None,
            "is_symlink": False,
        }

    return {
        "exists": True,
        "size": stat_result.st_size,
        "mtime_ns": stat_result.st_mtime_ns,
        "is_symlink": os.path.islink(item_path),
    }


class JournalLock:
    def __init__(self, journal_path):
        self.journal_path = journal_path
        self.lock_path = journal_path + ".lock"
        self.lock_fd = None

    def __enter__(self):
        started = time.monotonic()

        while True:
            try:
                self.lock_fd = os.open(self.lock_path, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
                os.write(self.lock_fd, str(os.getpid()).encode("utf-8"))
                fsync_file_descriptor(self.lock_fd)
                fsync_directory(os.path.dirname(self.lock_path))
                return self
            except FileExistsError:
                if time.monotonic() - started > LOCK_TIMEOUT_SECONDS:
                    raise TimeoutError("Could not acquire journal lock: " + self.lock_path)

                time.sleep(0.05)

    def __exit__(self, exc_type, exc_value, traceback):
        if self.lock_fd is not None:
            os.close(self.lock_fd)
            self.lock_fd = None

        try:
            os.unlink(self.lock_path)
            fsync_directory(os.path.dirname(self.lock_path))
        except FileNotFoundError:
            pass


def fsync_file_descriptor(file_descriptor):
    os.fsync(file_descriptor)


def fsync_directory(folder_path):
    if os.name == "nt":
        return

    try:
        directory_fd = os.open(folder_path, os.O_RDONLY)
    except OSError:
        return

    try:
        os.fsync(directory_fd)
    finally:
        os.close(directory_fd)


def append_journal_record(record):
    journal_path = get_journal_path()
    journal_folder = os.path.dirname(journal_path)
    os.makedirs(journal_folder, exist_ok=True)

    clean_record = {
        "journal_version": JOURNAL_VERSION,
        "timestamp": timestamp_now(),
    }
    clean_record.update(record)

    encoded_record = json.dumps(clean_record, sort_keys=True, ensure_ascii=False) + "\n"

    with JournalLock(journal_path):
        file_already_exists = os.path.exists(journal_path)

        with open(journal_path, "a", encoding="utf-8") as journal_file:
            journal_file.write(encoded_record)
            journal_file.flush()
            os.fsync(journal_file.fileno())

        if not file_already_exists:
            fsync_directory(journal_folder)

    return clean_record


def append_move_state(operation_id, batch_id, source_path, destination_path, state, extra=None):
    record = {
        "operation_id": operation_id,
        "batch_id": batch_id,
        "source_path": source_path,
        "destination_path": destination_path,
        "state": state,
        "source_metadata": get_path_metadata(source_path),
        "destination_metadata": get_path_metadata(destination_path),
    }

    if extra is not None:
        record["extra"] = extra

    return append_journal_record(record)


def read_journal_records():
    journal_path = get_journal_path()

    if not os.path.exists(journal_path):
        return []

    records = []

    with open(journal_path, "r", encoding="utf-8") as journal_file:
        for line_number, line in enumerate(journal_file, start=1):
            stripped_line = line.strip()

            if stripped_line == "":
                continue

            try:
                record = json.loads(stripped_line)
            except json.JSONDecodeError:
                records.append({
                    "journal_version": JOURNAL_VERSION,
                    "timestamp": timestamp_now(),
                    "state": "malformed_record",
                    "line_number": line_number,
                    "raw": stripped_line,
                })
                continue

            if not isinstance(record, dict):
                records.append({
                    "journal_version": JOURNAL_VERSION,
                    "timestamp": timestamp_now(),
                    "state": "malformed_record",
                    "line_number": line_number,
                    "raw": stripped_line,
                })
                continue

            records.append(record)

    return records


def get_latest_operation_records():
    operations = {}

    for record in read_journal_records():
        operation_id = record.get("operation_id")

        if operation_id is None:
            continue

        operations[operation_id] = record

    return operations
