from typing import List, Optional
from .models.task import Task, TaskStatus
from .storage.json_storage import JsonStorage
from pathlib import Path

storage_instance = JsonStorage(file_path=Path("json.db"))


class TaskService:

    def __init__(self, storage: JsonStorage):
        self._storage = storage

    def get_all_tasks(self) -> List[Task]
        return self._storage.get_all()
        
    def find_by_id(self, task_id: str) -> Optional[Task]:
        """Get a task by your id"""
        all_tasks = self._storage.get_all()
        for task in all_tasks:
            if task.id == task_id:
                return task
        return None

    def get_tasks_by_status(self, status: TaskStatus) -> List[Task]:
        all_tasks = self._storage.get_all()
        return [task for task in all_tasks if task.status == status]


    def 
