from datetime import datetime

from textual.app import ComposeResult
from textual.containers import Horizontal
from textual.widgets import Label, ListItem, ListView

from taskinder.models.task import Task, TaskStatus

STATUS_ICONS: dict[TaskStatus, str] = {
    TaskStatus.TODO: "󰄱",
    TaskStatus.DOING: "󰑓",
    TaskStatus.DONE: "󰄲",
}

STATUS_CLASSES: dict[TaskStatus, str] = {
    TaskStatus.TODO: "todo",
    TaskStatus.DOING: "doing",
    TaskStatus.DONE: "done",
}


def _relative_time(dt: datetime) -> str:
    delta = datetime.now() - dt
    total_secs = int(delta.total_seconds())
    if total_secs < 60:
        return "agora"
    if total_secs < 3600:
        return f"{total_secs // 60}m atrás"
    if delta.days == 0:
        return f"{total_secs // 3600}h atrás"
    if delta.days == 1:
        return "ontem"
    if delta.days < 7:
        return f"{delta.days}d atrás"
    return dt.strftime("%d/%m")


class TaskItem(ListItem):
    def __init__(self, task: Task) -> None:
        super().__init__()
        self.task = task
        self.add_class(STATUS_CLASSES[task.status])

    def compose(self) -> ComposeResult:
        icon = STATUS_ICONS[self.task.status]
        time_str = _relative_time(self.task.updated_at)
        desc = self.task.description[:45] + "…" if len(self.task.description) > 45 else self.task.description

        with Horizontal():
            yield Label(icon, classes="task-icon")
            yield Label(self.task.title, classes="task-title")
            yield Label(desc, classes="task-desc")
            yield Label(time_str, classes="task-time")

    def update_task(self, task: Task) -> None:
        self.task = task
        self.remove_class("todo", "doing", "done")
        self.add_class(STATUS_CLASSES[task.status])
        self.query_one(".task-icon", Label).update(STATUS_ICONS[task.status])
        self.query_one(".task-title", Label).update(task.title)
        time_str = _relative_time(task.updated_at)
        self.query_one(".task-time", Label).update(time_str)


class TaskListView(ListView):
    """Named subclass of ListView for CSS targeting."""
