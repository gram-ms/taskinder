import sqlite3
from pathlib import Path
from typing import List, Optional

from taskinder.models.task import Task, TaskStatus


class TaskRepository:
    def __init__(self, db_path: Path | str) -> None:
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(str(self.db_path))
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self) -> None:
        with self._connect() as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS tasks (
                    id TEXT PRIMARY KEY,
                    title TEXT NOT NULL,
                    description TEXT DEFAULT '',
                    status TEXT DEFAULT 'TODO',
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                )
            """)
            conn.commit()

    def _row_to_task(self, row: sqlite3.Row) -> Task:
        return Task.from_dict(dict(row))

    def get_all(self) -> List[Task]:
        with self._connect() as conn:
            rows = conn.execute(
                "SELECT * FROM tasks ORDER BY created_at DESC"
            ).fetchall()
        return [self._row_to_task(row) for row in rows]

    def add(self, task: Task) -> None:
        d = task.to_dict()
        with self._connect() as conn:
            conn.execute(
                "INSERT INTO tasks VALUES (?, ?, ?, ?, ?, ?)",
                (d["id"], d["title"], d["description"], d["status"],
                 d["created_at"], d["updated_at"]),
            )
            conn.commit()

    def find_by_id(self, task_id: str) -> Optional[Task]:
        with self._connect() as conn:
            row = conn.execute(
                "SELECT * FROM tasks WHERE id = ?", (task_id,)
            ).fetchone()
        return self._row_to_task(row) if row else None

    def find_by_title(self, task_title: str) -> List[Task]:
        with self._connect() as conn:
            rows = conn.execute(
                "SELECT * FROM tasks WHERE title = ?", (task_title,)
            ).fetchall()
        return [self._row_to_task(row) for row in rows]

    def find_by_status(self, status: TaskStatus) -> List[Task]:
        with self._connect() as conn:
            rows = conn.execute(
                "SELECT * FROM tasks WHERE status = ?", (status.value,)
            ).fetchall()
        return [self._row_to_task(row) for row in rows]

    def update(self, updated_task: Task) -> None:
        d = updated_task.to_dict()
        with self._connect() as conn:
            result = conn.execute(
                "UPDATE tasks SET title=?, description=?, status=?, updated_at=? WHERE id=?",
                (d["title"], d["description"], d["status"], d["updated_at"], d["id"]),
            )
            conn.commit()
        if result.rowcount == 0:
            raise ValueError(f"Task '{updated_task.id}' not found.")

    def delete(self, task_id: str) -> None:
        with self._connect() as conn:
            result = conn.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
            conn.commit()
        if result.rowcount == 0:
            raise ValueError(f"Task '{task_id}' not found.")

    def count(self) -> dict[str, int]:
        counts: dict[str, int] = {"TODO": 0, "DOING": 0, "DONE": 0}
        with self._connect() as conn:
            rows = conn.execute(
                "SELECT status, COUNT(*) as cnt FROM tasks GROUP BY status"
            ).fetchall()
        for row in rows:
            counts[row["status"]] = row["cnt"]
        return counts
