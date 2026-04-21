from __future__ import annotations

from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Horizontal, Vertical
from textual.screen import ModalScreen
from textual.widgets import Button, Input, Label, Select, TextArea

from taskinder.models.task import Task, TaskStatus


class EditScreen(ModalScreen[bool]):
    BINDINGS = [
        Binding("ctrl+s", "save", "Salvar"),
        Binding("escape", "cancel", "Cancelar"),
    ]

    DEFAULT_CSS = """
    EditScreen {
        align: center middle;
        background: $background 70%;
    }
    #edit-dialog {
        width: 72;
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
    }
    #edit-dialog Label {
        color: $foreground;
        margin-bottom: 0;
    }
    #input-title {
        margin-bottom: 1;
    }
    #input-desc {
        height: 5;
        margin-bottom: 1;
    }
    #input-status {
        margin-bottom: 1;
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
        self.task = task

    @property
    def is_editing(self) -> bool:
        return self.task is not None

    def compose(self) -> ComposeResult:
        title_val = self.task.title if self.task else ""
        desc_val = self.task.description if self.task else ""
        status_val = self.task.status if self.task else TaskStatus.TODO
        heading = "✎  Editar Tarefa" if self.is_editing else "  Nova Tarefa"

        with Vertical(id="edit-dialog"):
            yield Label(heading, id="edit-heading")
            yield Label("Título")
            yield Input(value=title_val, placeholder="Título da tarefa...", id="input-title")
            yield Label("Descrição")
            yield TextArea(text=desc_val, id="input-desc")
            yield Label("Status")
            yield Select(
                options=[(s.value, s) for s in TaskStatus],
                value=status_val,
                id="input-status",
            )
            with Horizontal(id="edit-buttons"):
                yield Button("Salvar", variant="primary", id="btn-save")
                yield Button("Cancelar", id="btn-cancel")

    def on_mount(self) -> None:
        self.query_one("#input-title", Input).focus()

    def action_save(self) -> None:
        title = self.query_one("#input-title", Input).value.strip()
        if not title:
            self.query_one("#input-title", Input).focus()
            self.app.notify("O título não pode ser vazio.", severity="error")
            return

        desc = self.query_one("#input-desc", TextArea).text.strip()
        status_raw = self.query_one("#input-status", Select).value
        status = status_raw if isinstance(status_raw, TaskStatus) else TaskStatus(str(status_raw))

        service = self.app.service  # type: ignore[attr-defined]
        if self.is_editing:
            service.update_task_by_id(self.task.id, title=title, description=desc, status=status)
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
