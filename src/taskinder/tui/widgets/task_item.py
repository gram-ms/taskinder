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
    def __init__(self, *children: ListItem, **kwargs) -> None:
        super().__init__(*children, initial_index=None, **kwargs)

    @property
    def has_overflow(self) -> bool:
        return self.virtual_size.height > self.size.height

    @property
    def allow_vertical_scroll(self) -> bool:
        return self.has_overflow and super().allow_vertical_scroll

    def _reset_scroll(self) -> None:
        self.scroll_y = 0
        self.scroll_target_y = 0

    def refresh_scroll_state(self) -> None:
        overflow_y = "auto" if self.has_overflow else "hidden"
        if self.styles.overflow_y != overflow_y:
            self.styles.overflow_y = overflow_y
        if not self.has_overflow:
            self._reset_scroll()

    def sync_state(self) -> None:
        self.refresh_scroll_state()
        next_index = self.index if self._is_valid_index(self.index) else (0 if self.children else None)
        if self.index != next_index:
            self.index = next_index

    def action_cursor_down(self) -> None:
        if not self.has_overflow:
            return
        super().action_cursor_down()

    def action_cursor_up(self) -> None:
        if not self.has_overflow:
            return
        super().action_cursor_up()

    def on_mount(self) -> None:
        self.call_after_refresh(self.sync_state)

    def on_resize(self) -> None:
        self.call_after_refresh(self.sync_state)
