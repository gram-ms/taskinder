from datetime import datetime

from textual.app import ComposeResult
from textual.containers import Horizontal, Vertical
from textual.widgets import Label, ListItem, ListView

from taskinder.models.task import Task, TaskStatus

STATUS_ICONS: dict[TaskStatus, str] = {
    TaskStatus.TODO: "󰄱",
    TaskStatus.DOING: "󰑓",
    TaskStatus.DONE: "󰄲",
}

STATUS_LABELS: dict[TaskStatus, str] = {
    TaskStatus.TODO: "todo",
    TaskStatus.DOING: "doing",
    TaskStatus.DONE: "done",
}


def _relative_time(dt: datetime) -> str:
    delta = datetime.now() - dt
    secs = int(delta.total_seconds())
    if secs < 60:
        return "agora"
    if secs < 3600:
        return f"{secs // 60}m"
    if delta.days == 0:
        return f"{secs // 3600}h"
    if delta.days == 1:
        return "ontem"
    if delta.days < 7:
        return f"{delta.days}d"
    return dt.strftime("%d/%m")


class TaskItem(ListItem):
    def __init__(self, task: Task) -> None:
        super().__init__()
        # double-underscore to avoid conflict with Widget._task / Widget.task (asyncio)
        self.__record = task
        self.add_class(STATUS_LABELS[task.status])

    @property
    def data(self) -> Task:
        return self.__record

    def compose(self) -> ComposeResult:
        t = self.__record
        icon = STATUS_ICONS[t.status]
        time_str = _relative_time(t.updated_at)
        desc = (t.description[:60] + "…") if len(t.description) > 60 else t.description

        with Vertical(classes="item-body"):
            with Horizontal(classes="item-row-main"):
                yield Label(icon, classes="task-icon")
                yield Label(t.title, classes="task-title")
                yield Label(time_str, classes="task-time")
            if desc:
                with Horizontal(classes="item-row-desc"):
                    yield Label("", classes="task-icon-spacer")
                    yield Label(desc, classes="task-desc")


class TaskListView(ListView):
    pass
