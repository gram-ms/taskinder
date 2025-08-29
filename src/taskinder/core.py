from typing import List, Optional
from .models.task import Task, TaskStatus
from .storage.task_repository import TaskRepository


class TaskService:
    def __init__(self, repository: TaskRepository):
        self._repository = repository

    def get_all_tasks(self) -> List[Task]:
        return self._repository.get_all()

    def get_task_by_id(self, task_id: int) -> Optional[Task]:
        """Get a task by its id."""
        return self._repository.find_by_id(task_id)

    def get_task_by_title(self, task_title: str) -> List[Task]:
        """Get tasks by their title."""
        return self._repository.find_by_title(task_title)

    def get_task_by_status(self, status: TaskStatus) -> List[Task]:
        if not isinstance(status, TaskStatus):
            raise TypeError(
                f"The status must be a TaskStatus object, not {type(status)}"
            )
        return self._repository.find_by_status(status)

    def create_task(self, title: str, description: str) -> Task:
        """Creates a new task."""
        if not title:
            raise ValueError("Title cannot be empty.")

        new_id = self._repository.get_new_id()
        new_task = Task(id=new_id, title=title, description=description)
        self._repository.add(new_task)
        return new_task

    def update_task_by_id(
        self,
        task_id: int,
        title: Optional[str] = None,
        description: Optional[str] = None,
        status: Optional[TaskStatus] = None,
    ) -> Optional[Task]:
        """Updates a task's attributes."""
        task = self.get_task_by_id(task_id)
        if not task:
            return None

        if title is not None:
            task.update_title(title)
        if description is not None:
            task.description = description
        if status is not None:
            task.update_status(status)

        self._repository.update(task)
        return task

    def delete_task_by_id(self, task_id: int) -> bool:
        """Deletes a task by its ID."""
        return self._repository.delete(task_id)
