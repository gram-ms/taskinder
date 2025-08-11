from pathlib import Path
from typing import List, Dict, Any, Optional
from ..models.task import Task, TaskStatus
import json

JsonData = List[Dict[str, Any]]


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
            with open(self.file_path, "w", encoding="utf-8") as _file:
                json.dump([], _file)

    def _load_data(self) -> JsonData:
        """Loads raw data from the JSON file."""
        try:
            with open(self.file_path, "r", encoding="utf-8") as _file:
                if self.file_path.stat().st_size == 0:
                    return []
                data = json.load(_file)
            if not isinstance(data, list):
                raise TypeError(f"Data in {self.file_path} is not a list.")
            return data
        except json.JSONDecodeError as e:
            raise ValueError(f"Error decoding JSON from {self.file_path}: {e}")
        except (TypeError, IOError) as e:
            raise ValueError(f"Error loading data from {self.file_path}: {e}")

    def _save_data(self, data: JsonData) -> None:
        """Save raw data to the JSON file."""
        try:
            with open(self.file_path, "w", encoding="utf-8") as file_:
                json.dump(data, file_, indent=4, ensure_ascii=False)
        except IOError as e:
            raise ValueError(f"Error saving data to {self.file_path}: {e}")

    def get_all(self) -> List[Task]:
        """
        Loads all tasks from the JSON file and converts them to Task objects.
        """
        raw_data = self._load_data()
        return [Task.from_dict(item) for item in raw_data]

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
        This is less efficient than 'save_all' for multiple additions.
        """
        all_tasks = self.get_all()
        all_tasks.append(task)
        self.save_all(all_tasks)

    def find_by_id(self, task_id: str) -> Optional[Task]:
        """Finds a task by its ID."""
        return next((task for task in self.get_all() if task.id == task_id), None)

    def find_by_title(self, task_title: str) -> List[Task]:
        """Finds all tasks with a given title."""
        return [task for task in self.get_all() if task.title == task_title]

    def find_by_status(self, status: TaskStatus) -> List[Task]:
        """Finds all tasks with a given status."""
        return [task for task in self.get_all() if task.status == status]

    def update(self, updated_task: Task) -> None:
        """Updates an existing task in the JSON file."""
        all_tasks = self.get_all()
        task_found = False
        for i, task in enumerate(all_tasks):
            if task.id == updated_task.id:
                all_tasks[i] = updated_task
                task_found = True
                break
        if not task_found:
            raise ValueError(f"Task with ID '{updated_task.id}' not found.")
        self.save_all(all_tasks)

    def delete(self, task_id: str) -> None:
        """Deletes a task by its ID."""
        all_tasks = self.get_all()
        original_count = len(all_tasks)
        tasks_to_keep = [task for task in all_tasks if task.id != task_id]

        if len(tasks_to_keep) == original_count:
            raise ValueError(f"Task with ID '{task_id}' not found.")

        self.save_all(tasks_to_keep)
