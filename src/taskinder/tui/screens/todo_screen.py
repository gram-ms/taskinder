from __future__ import annotations

from pathlib import Path

from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Vertical
from textual.screen import ModalScreen
from textual.widgets import DataTable, Footer, Label


class TodoScreen(ModalScreen[bool]):
    BINDINGS = [
        Binding("escape", "cancel", "Voltar"),
        Binding("j", "cursor_down", "Baixo", show=False),
        Binding("k", "cursor_up", "Cima", show=False),
        Binding("i", "import_task", "Importar como task"),
    ]

    DEFAULT_CSS = """
    TodoScreen {
        align: center middle;
        background: $background 70%;
    }
    #todo-dialog {
        width: 95%;
        height: 80%;
        background: $surface;
        border: heavy $primary;
        padding: 1 2;
    }
    #todo-heading {
        color: $primary;
        text-style: bold;
        text-align: center;
        margin-bottom: 1;
    }
    #todo-table {
        height: 1fr;
    }
    #todo-hint {
        color: $text-muted;
        text-style: dim;
        text-align: center;
        margin-top: 1;
    }
    """

    def __init__(self, project_dir: Path) -> None:
        super().__init__()
        self.project_dir = project_dir

    def compose(self) -> ComposeResult:
        with Vertical(id="todo-dialog"):
            yield Label("  Escaneando TODOs…", id="todo-heading")
            yield DataTable(id="todo-table", cursor_type="row")
            yield Label("i: importar como task · esc: voltar", id="todo-hint")
        yield Footer()

    def on_mount(self) -> None:
        from taskinder.scanner.todo_scanner import TodoScanner

        table = self.query_one("#todo-table", DataTable)
        table.add_columns("Tipo", "Arquivo", "Linha", "Texto")

        scanner = TodoScanner()
        items = scanner.scan(self.project_dir)

        if items:
            for item in items:
                table.add_row(item.kind, item.file, str(item.line), item.text)
            count = len(items)
            self.query_one("#todo-heading", Label).update(
                f"  {count} item{'s' if count > 1 else ''} encontrado{'s' if count > 1 else ''}"
            )
        else:
            self.query_one("#todo-heading", Label).update("  Nenhum TODO encontrado")

    def action_cursor_down(self) -> None:
        self.query_one("#todo-table", DataTable).action_scroll_down()

    def action_cursor_up(self) -> None:
        self.query_one("#todo-table", DataTable).action_scroll_up()

    def action_import_task(self) -> None:
        table = self.query_one("#todo-table", DataTable)
        if table.row_count == 0:
            return
        row_key, _ = table.coordinate_to_cell_key(table.cursor_coordinate)
        row_data = table.get_row(row_key)
        kind, file_, line, text = row_data[0], row_data[1], row_data[2], row_data[3]
        title = f"{kind}: {text}"
        desc = f"De {file_}:{line}"
        self.app.service.create_task(title, desc)  # type: ignore[attr-defined]
        self.app.notify(f"Task criada: {title[:50]}")

    def action_cancel(self) -> None:
        self.dismiss(False)
