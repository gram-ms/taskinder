from __future__ import annotations

from pathlib import Path

from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Vertical
from textual.screen import ModalScreen
from textual.widgets import DataTable, Footer, Label


class TodoScreen(ModalScreen[bool]):
    BINDINGS = [
        Binding("escape", "cancel", "Back"),
        Binding("j", "move_down", "Down", show=False),
        Binding("k", "move_up", "Up", show=False),
        Binding("i", "import_task", "Import"),
    ]

    DEFAULT_CSS = """
    TodoScreen {
        align: center middle;
        background: $background 70%;
    }
    #scan-dialog {
        width: 95%;
        height: 80%;
        background: $surface;
        border: heavy $primary;
        padding: 1 2;
    }
    #scan-heading {
        color: $primary;
        text-style: bold;
        text-align: center;
        margin-bottom: 1;
    }
    #scan-table {
        height: 1fr;
    }
    #scan-hint {
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
        with Vertical(id="scan-dialog"):
            yield Label("  Scanning for TODOs…", id="scan-heading")
            yield DataTable(id="scan-table", cursor_type="row")
            yield Label("i: import as task  ·  esc: back", id="scan-hint")
        yield Footer()

    def on_mount(self) -> None:
        from taskinder.scanner.todo_scanner import TodoScanner

        table = self.query_one("#scan-table", DataTable)
        table.add_columns("Kind", "File", "Line", "Text")

        scanner = TodoScanner()
        items = scanner.scan(self.project_dir)

        if items:
            for item in items:
                table.add_row(item.kind, item.file, str(item.line), item.text)
            count = len(items)
            self.query_one("#scan-heading", Label).update(
                f"  {count} item{'s' if count != 1 else ''} found"
            )
        else:
            self.query_one("#scan-heading", Label).update("  No TODOs found")

    def action_move_down(self) -> None:
        self.query_one("#scan-table", DataTable).action_scroll_down()

    def action_move_up(self) -> None:
        self.query_one("#scan-table", DataTable).action_scroll_up()

    def action_import_task(self) -> None:
        table = self.query_one("#scan-table", DataTable)
        if table.row_count == 0:
            return
        row_key, _ = table.coordinate_to_cell_key(table.cursor_coordinate)
        row_data = table.get_row(row_key)
        kind, file_, line, text = row_data[0], row_data[1], row_data[2], row_data[3]
        title = f"{kind}: {text}"
        desc = f"From {file_}:{line}"
        self.app.service.create_task(title, desc)  # type: ignore[attr-defined]
        self.app.notify(f"Task created: {title[:50]}")

    def action_cancel(self) -> None:
        self.dismiss(False)
