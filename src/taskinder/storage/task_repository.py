from pathlib import Path
from typing import List, Dict, Any, Optional
from ..models.task import Task, TaskStatus
import json

JsonData = Dict[str, Any]


# pattern example
# {
#     "last_id": 0,
#     "tasks": [
#         { "id": 1, "title": "task 1", ...}
#     ]
# }


class TaskRepository:
    """
    Manages storage of Task objects in a JSON file.
    This class acts as a Repository, responsible for the 'translation'
    layer between Task objects in memory and the JSON file data source.
    """

    def __init__(self, file_path: Path | str) -> None:
        self.file_path = Path(file_path)
        self.file_path.parent.mkdir(parents=True, exist_ok=True)
        if not self.file_path.exists():
            self._save_data({"last_id": 0, "tasks": []})

    def _load_data(self) -> JsonData:
        """Loads raw data from the JSON file."""
        try:
            with open(self.file_path, "r", encoding="utf-8") as _file:
                if self.file_path.stat().st_size == 0:
                    return {"last_id": 0, "tasks": []}
                data = json.load(_file)
            if (
                not isinstance(data, dict)
                or "tasks" not in data
                or "last_id" not in data
            ):
                raise TypeError(f"Data in {self.file_path}, invalid structure")
            return data
        except (json.JSONDecodeError, TypeError, IOError) as e:
            raise ValueError(f"Error loading data from {self.file_path}: {e}")

    def _save_data(self, data: JsonData) -> None:
        """Save raw data to the JSON file."""
        try:
            with open(self.file_path, "w", encoding="utf-8") as file_:
                json.dump(data, file_, indent=4, ensure_ascii=False)
        except IOError as e:
            raise ValueError(f"Error saving data to {self.file_path}: {e}")

    def get_new_id(self) -> int:
        """Gets a new ID and increments the counter."""
        data = self._load_data()
        if len(data["tasks"]) == 0:
            new_id = 1           
        else:
            new_id = data["last_id"] + 1
        data["last_id"] = new_id
        self._save_data(data)
        return new_id

    def get_all(self) -> List[Task]:
        """
        Loads all tasks from the JSON file and converts them to Task objects.
        """
        raw_data = self._load_data()
        return [Task.from_dict(item) for item in raw_data["tasks"]]

    def save_all(self, tasks: List[Task]) -> None:
        """
        Convert a list of Task objects to a dictionary and save it to the file,
        overwriting the previous content.
        """
        raw_data = [task.to_dict() for task in tasks]
        self._save_data(raw_data)

    def add(self, task: Task) -> None:
        """
        Adds a single task to the JSON file.
        """
        data = self._load_data()
        data["tasks"].append(task.to_dict())
        self._save_data(data)

    def find_by_id(self, task_id: int) -> Optional[Task]:
        """Finds a task by its ID."""
        for task_data in self._load_data()["tasks"]:
            if task_data["id"] == task_id:
                return Task.from_dict(task_data)
        return None

    def find_by_title(self, task_title: str) -> List[Task]:
        """Finds all tasks with a given title."""
        return [
            Task.from_dict(t)
            for t in self._load_data()["tasks"]
            if t["title"] == task_title
        ]

    def find_by_status(self, status: TaskStatus) -> List[Task]:
        """Finds all tasks with a given status."""
        return [
            Task.from_dict(t)
            for t in self._load_data()["tasks"]
            if t["status"] == status.value
        ]

    def update(self, updated_task: Task) -> None:
        """Updates an existing task in the JSON file."""
        data = self._load_data()
        task_found = False
        for n, task_data in enumerate(data["tasks"]):
            if task_data["id"] == updated_task.id:
                data["tasks"][n] = updated_task.to_dict()
                task_found = True
                break
        if not task_found:
            raise ValueError(f"Task with ID '{updated_task.id}' not found.")
        self._save_data(data)

    def delete(self, task_id: int) -> bool:
        """Deletes a task by ID."""
        data = self._load_data()
        original_count = len(data["tasks"])
        tasks_to_keep = [task for task in data["tasks"] if task["id"] != task_id]

        if len(tasks_to_keep) == original_count:
            return False  # Nothing was deleted

        data["tasks"] = tasks_to_keep
        self._save_data(data)
        return True
