from pathlib import Path
from typing import List, Dict, Any
from ..models.task import Task
import json

# Define a especific type for the JSON data
JsonData = List[Dict[str, Any]]


class JsonStorage:
    """Manages storage of Task objects in a JSON file.
    This class is responsible for the 'translation' layer between
    Task objects in memory and JSON file.
    """

    def __init__(self, file_path: Path | str) -> None:
        self.file_path = Path(file_path)
        self.file_path.parent.mkdir(parents=True, exist_ok=True)
        if not self.file_path.exists():
            # Create a file with an empty list if it doesnt exist
            with open(self.file_path, 'w', encoding='utf-8') as _file:
                json.dump([], _file)

    def _load_data(self) -> JsonData:
        """Loads raw data from the JSON file"""
        try:
            with open(self.file_path, 'r', encoding='utf-8') as _file:
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
        """Save raw data to teh JSON file"""
        try:
            with open(self.file_path, "w", encoding="utf-8") as file_:
                json.dump(data, file_, indent=4, ensure_ascii=False)
        except IOError as e:
            raise ValueError(f"Error saving data to {self.file_path}: {e}")

    def get_all(self) -> List[Task]:
        """
        Loads all tasks from the JSON file and converts to Task
        """
        raw_data = self._load_data()
        return [Task.from_dict(item) for item in raw_data]

    def save_all(self, tasks: List[Task]) -> None:
        """
        Converts a list of Task objects to dictionary and saves to the file,
        overwriting the previous content.
        """
        raw_data = [task.to_dict() for task in tasks]
        self._save_data(raw_data)

    def add(self, task: Task) -> None:
        """
        Add a single task to the JSON file.
        This is less e efficient than 'save_all' for multiple additions.
        """
        all_tasks = self.get_all()
        all_tasks.append(task)
        self.save_all(all_tasks)
