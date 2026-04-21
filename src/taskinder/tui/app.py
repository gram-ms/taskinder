from __future__ import annotations

from pathlib import Path

from textual.app import App, ComposeResult
from textual.binding import Binding

from taskinder.core import TaskService
from taskinder.storage.task_repository import TaskRepository
from taskinder.tui.themes.manager import ThemeManager


class TaskinderApp(App):
    TITLE = "Taskinder"
    SUB_TITLE = "Gerenciador de tarefas por projeto"

    BINDINGS = [
        Binding("ctrl+q", "quit", "Sair", show=False),
    ]

    DEFAULT_CSS = """
    Screen {
        background: $background;
    }
    """

    def __init__(self, project_dir: Path | None = None) -> None:
        super().__init__()
        self.project_dir = project_dir or Path.cwd()
        db_path = self.project_dir / ".taskinder" / "tasks.db"
        self.repository = TaskRepository(db_path)
        self.service = TaskService(self.repository)
        self.theme_manager = ThemeManager()

    def on_mount(self) -> None:
        for theme in self.theme_manager.get_all_themes():
            try:
                self.register_theme(theme)
            except Exception:
                pass

        active = self.theme_manager.get_active_theme_name()
        try:
            self.theme = active
        except Exception:
            pass

        from taskinder.tui.screens.main_screen import MainScreen
        self.push_screen(MainScreen())
