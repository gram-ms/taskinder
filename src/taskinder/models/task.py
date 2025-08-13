from dataclasses import dataclass, asdict, field
from enum import Enum
from datetime import datetime


class TaskStatus(Enum):
    TODO = "TODO"
    DOING = "DOING"
    DONE = "DONE"


@dataclass
class Task:
    """Represents a task in the task management system."""

    id: str
    title: str
    description: str
    status: TaskStatus = TaskStatus.TODO
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)

    def __post_init__(self):
        if isinstance(self.status, str):
            self.status = TaskStatus(self.status)

    def update_status(self, new_status: TaskStatus):
        """Update the status of the task and timestamp."""
        self.status = new_status
        self.updated_at = datetime.now()

    def update_title(self, new_title: str):
        """Update the title of the task"""
        self.title = new_title
        self.updated_at = datetime.now()

    def to_dict(self) -> dict:
        """Convert the task to a dictionary, ready for serialization."""
        data = asdict(self)
        data["status"] = self.status.value
        data["created_at"] = self.created_at.isoformat()
        data["updated_at"] = self.updated_at.isoformat()
        return data

    @classmethod
    def from_dict(cls, data: dict) -> "Task":
        "Creates a instance of Task from dict."
        data["status"] = TaskStatus(data["status"])
        data["created_at"] = datetime.fromisoformat(data["created_at"])
        data["updated_at"] = datetime.fromisoformat(data["updated_at"])
        return cls(**data)
