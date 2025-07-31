from pathlib import Path
from typing import List, Dict, Any
import json

# Define a especific type for the JSON data
JsonData = List[Dict[str, Any]]


class JsonStorage:
    """Manages storage of data in a JSON file.
    This class is responsible for loading and saving data to a JSON file.
    Ensures that the file has a list of data items.
    """

    def __init__(self, file_path: Path | str) -> None:
        self.file_path = Path(file_path)
        self._data: JsonData = []
        self.file_path.parent.mkdir(parents=True, exist_ok=True)
        self._data = self._load_data()

    def _load_data(self) -> JsonData:
        """
        Load data from the JSON File
        Returns:
            JsonData: A list of dictionaries representing the data.
        Raises:
            ValueError: If the file is empty or contains invalid JSON.
            TypeError: If the data is not a list.
            Exception: For any other errors during file operations.
        """
        if not self.file_path.exists():
            return []
        try:
            if self.file_path.stat().st_size == 0:
                return []
            with open(self.file_path, "r", encoding="utf-8") as file_:
                data = json.load(file_)
            if not isinstance(data, list):
                raise TypeError(f"Data in {self.file_path} is not a list.")
            return data
        except json.JSONDecodeError as e:
            raise ValueError(f"Error decoding JSON from {self.file_path}: {e}")
        except (TypeError, Exception) as e:
            raise ValueError(f"Error loading data from {self.file_path}: {e}")

    def _save_data(self) -> None:
        """Save tthe list of current data (self._data) to the JSON file."""
        try:
            with open(self.file_path, "w", encoding="utf-8") as file_:
                json.dump(self._data, file_, indent=4, ensure_ascii=False)
        except Exception as e:
            raise ValueError(f"Error saving data to {self.file_path}: {e}")

    def get_current_data(self) -> JsonData:
        """Return a copy of all items in the storage."""
        return self._data.copy()

    def add_item(self, item: Dict[str, Any]) -> None:
        """
        Add a new item to the list and persist it to the JSON file.
        args:
            item (Dict[str, any]): The item to add
        """
        self._data.append(item)
        self._save_data()
