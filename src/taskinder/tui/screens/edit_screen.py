from __future__ import annotations

from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Horizontal, Vertical
from textual.screen import ModalScreen
from textual.widgets import Button, Input, Label, Select, TextArea

from taskinder.models.task import Task, TaskStatus


class EditScreen(ModalScreen[bool]):
    BINDINGS = [
        Binding("ctrl+s", "save", "Save"),
        Binding("escape", "cancel", "Cancel"),
    ]

    DEFAULT_CSS = """
    EditScreen {
        align: center middle;
        background: $background 75%;
    }
    #edit-dialog {
        width: 68;
        height: auto;
        background: $surface;
        border: heavy $primary;
        padding: 1 2;
    }
    #edit-heading {
        text-style: bold;
        color: $primary;
        text-align: center;
        margin-bottom: 1;
        padding: 0 1;
    }
    #edit-dialog Label.field-label {
        color: $text-muted;
        text-style: dim;
        margin-top: 1;
        margin-bottom: 0;
    }
    #input-title {
        margin-bottom: 0;
    }
    #input-desc {
        height: 4;
        margin-bottom: 0;
    }
    #input-status {
        margin-bottom: 0;
    }
    #edit-buttons {
        align-horizontal: right;
        margin-top: 1;
        height: 3;
    }
    #edit-buttons Button {
        margin-left: 1;
    }
    """

    def __init__(self, task: Task | None = None) -> None:
        super().__init__()
        # double-underscore avoids conflict with Widget.task / Widget._task (asyncio)
        self.__source = task

    @property
    def is_editing(self) -> bool:
        return self.__source is not None

    def compose(self) -> ComposeResult:
        title_val = self.__source.title if self.__source else ""
        desc_val = self.__source.description if self.__source else ""
        status_val = self.__source.status if self.__source else TaskStatus.TODO
        heading = "󰏫  Edit Task" if self.is_editing else "  New Task"

        with Vertical(id="edit-dialog"):
            yield Label(heading, id="edit-heading")
            yield Label("Title", classes="field-label")
            yield Input(value=title_val, placeholder="What needs to be done?", id="input-title")
            yield Label("Description", classes="field-label")
            yield TextArea(text=desc_val, id="input-desc")
            yield Label("Status", classes="field-label")
            yield Select(
                options=[(s.value, s) for s in TaskStatus],
                value=status_val,
                id="input-status",
            )
            with Horizontal(id="edit-buttons"):
                yield Button("  Save", variant="primary", id="btn-save")
                yield Button("  Cancel", id="btn-cancel")

    def on_mount(self) -> None:
        self.query_one("#input-title", Input).focus()

    def action_save(self) -> None:
        title = self.query_one("#input-title", Input).value.strip()
        if not title:
            self.query_one("#input-title", Input).focus()
            self.app.notify("Title cannot be empty.", severity="error")
            return

        desc = self.query_one("#input-desc", TextArea).text.strip()
        status_raw = self.query_one("#input-status", Select).value
        status = status_raw if isinstance(status_raw, TaskStatus) else TaskStatus(str(status_raw))

        service = self.app.service  # type: ignore[attr-defined]
        if self.is_editing:
            service.update_task_by_id(self.__source.id, title=title, description=desc, status=status)
        else:
            new_task = service.create_task(title, desc)
            if status != TaskStatus.TODO:
                service.update_task_by_id(new_task.id, status=status)

        self.dismiss(True)

    def action_cancel(self) -> None:
        self.dismiss(False)

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "btn-save":
            self.action_save()
        else:
            self.action_cancel()
