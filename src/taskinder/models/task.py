from dataclasses import dataclass
from enum import Enum
from datetime import datetime


class TaskStatus(Enum):
    TODO = "TODO"
    DOING = "DOING"
    DONE = "DONE"


@dataclass
class Task:
    """Represents a task in the task management system."""
    id: int  # Unique identifier for the task
    title: str  # Title of the task
    description: str  # Description of the task
    status: TaskStatus = TaskStatus.TODO  # Current status of the task
    created_at: datetime = datetime.now()  # Timestamp when the task created
    updated_at: datetime = datetime.now()  # Timestamp last updated

    def __post_init__(self):
        """Post-initialization checks to ensure data integrity."""
        if not isinstance(self.status, TaskStatus):
            raise ValueError("status must be an instance of TaskStatus Enum")
        if not isinstance(self.created_at, datetime):
            raise ValueError("created_at must be a datetime instance")
        if not isinstance(self.updated_at, datetime):
            raise ValueError("updated_at must be a datetime instance")

    def update_status(self, new_status: TaskStatus):
        """Update the status of the task."""
        if not isinstance(new_status, TaskStatus):
            raise ValueError("new_status must be an instance of TaskStatus")

        self.status = new_status
        self.updated_at = datetime.now()  # Update the timestamp
