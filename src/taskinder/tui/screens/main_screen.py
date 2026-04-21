from __future__ import annotations

from pathlib import Path

from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Vertical
from textual.screen import Screen
from textual.widgets import Footer, Label, Static, TabbedContent, TabPane

from taskinder.models.task import Task, TaskStatus
from taskinder.tui.widgets.task_item import TaskItem, TaskListView


class ProjectHeader(Static):
    DEFAULT_CSS = """
    ProjectHeader {
        height: 4;
        padding: 0 2;
        background: $panel;
        border-bottom: heavy $primary;
        layout: vertical;
        content-align: left middle;
    }
    #header-title {
        color: $primary;
        text-style: bold;
    }
    #header-stats {
        color: $text-muted;
    }
    """

    def compose(self) -> ComposeResult:
        cwd = Path.cwd()
        try:
            display = "~/" + str(cwd.relative_to(Path.home()))
        except ValueError:
            display = str(cwd)
        yield Label(f"  Taskinder  ·  {display}", id="header-title")
        yield Label("Carregando…", id="header-stats")

    def update_counts(self, counts: dict[str, int]) -> None:
        todo = counts.get("TODO", 0)
        doing = counts.get("DOING", 0)
        done = counts.get("DONE", 0)
        self.query_one("#header-stats", Label).update(
            f"󰄱  {todo} todo    󰑓  {doing} em progresso    󰄲  {done} concluído"
        )


class MainScreen(Screen):
    BINDINGS = [
        Binding("j", "cursor_down", "Baixo", show=False),
        Binding("k", "cursor_up", "Cima", show=False),
        Binding("down", "cursor_down", show=False),
        Binding("up", "cursor_up", show=False),
        Binding("n", "new_task", "Nova"),
        Binding("e", "edit_task", "Editar"),
        Binding("d", "delete_task", "Deletar"),
        Binding("space", "toggle_status", "Toggle"),
        Binding("enter", "toggle_status", show=False),
        Binding("t", "scan_todos", "TODOs"),
        Binding("T", "switch_theme", "Tema"),
        Binding("q", "app.quit", "Sair"),
        Binding("question_mark", "show_help", "Ajuda", show=False),
        Binding("1", "filter_tab('all')", show=False),
        Binding("2", "filter_tab('todo')", show=False),
        Binding("3", "filter_tab('doing')", show=False),
        Binding("4", "filter_tab('done')", show=False),
    ]

    DEFAULT_CSS = """
    MainScreen {
        background: $background;
        layout: vertical;
    }
    TabbedContent {
        height: 1fr;
    }
    TabPane {
        padding: 0;
        background: $background;
    }
    TaskListView {
        background: $background;
        height: 1fr;
    }
    TaskItem {
        height: 3;
        padding: 0 1;
        border-left: blank $panel;
        layout: vertical;
    }
    TaskItem:hover {
        background: $surface;
    }
    TaskItem.--highlight {
        background: $surface;
        border-left: heavy $primary;
    }
    TaskItem > Horizontal {
        height: 100%;
        align-vertical: middle;
    }
    .task-icon {
        width: 3;
        content-align: left middle;
        text-style: bold;
    }
    TaskItem.todo .task-icon { color: $warning; }
    TaskItem.doing .task-icon { color: $secondary; }
    TaskItem.done .task-icon { color: $success; }
    .task-title {
        width: 1fr;
        content-align: left middle;
        color: $foreground;
    }
    TaskItem.done .task-title {
        color: $text-muted;
        text-style: dim strike;
    }
    .task-desc {
        width: 35;
        content-align: left middle;
        color: $text-muted;
        text-style: dim;
    }
    .task-time {
        width: 12;
        content-align: right middle;
        color: $text-muted;
        text-style: dim;
    }
    """

    def compose(self) -> ComposeResult:
        yield ProjectHeader()
        with TabbedContent(initial="all"):
            with TabPane("Todas", id="all"):
                yield TaskListView(id="list-all")
            with TabPane("Todo", id="todo"):
                yield TaskListView(id="list-todo")
            with TabPane("Em progresso", id="doing"):
                yield TaskListView(id="list-doing")
            with TabPane("Concluídas", id="done"):
                yield TaskListView(id="list-done")
        yield Footer()

    def on_mount(self) -> None:
        self.refresh_tasks()

    def _active_list(self) -> TaskListView:
        active = self.query_one(TabbedContent).active
        return self.query_one(f"#list-{active}", TaskListView)

    def _selected_task(self) -> Task | None:
        item = self._active_list().highlighted_child
        if isinstance(item, TaskItem):
            return item.task
        return None

    def refresh_tasks(self) -> None:
        service = self.app.service  # type: ignore[attr-defined]
        repo = self.app.repository  # type: ignore[attr-defined]
        tasks = service.get_all_tasks()
        counts = repo.count()
        self.query_one(ProjectHeader).update_counts(counts)

        groups: dict[str, list[Task]] = {
            "all": tasks,
            "todo": [t for t in tasks if t.status == TaskStatus.TODO],
            "doing": [t for t in tasks if t.status == TaskStatus.DOING],
            "done": [t for t in tasks if t.status == TaskStatus.DONE],
        }
        for tab_id, task_list in groups.items():
            lv = self.query_one(f"#list-{tab_id}", TaskListView)
            lv.clear()
            for task in task_list:
                lv.append(TaskItem(task))

    def action_cursor_down(self) -> None:
        self._active_list().action_cursor_down()

    def action_cursor_up(self) -> None:
        self._active_list().action_cursor_up()

    def action_toggle_status(self) -> None:
        task = self._selected_task()
        if not task:
            return
        next_map = {
            TaskStatus.TODO: TaskStatus.DOING,
            TaskStatus.DOING: TaskStatus.DONE,
            TaskStatus.DONE: TaskStatus.TODO,
        }
        self.app.service.update_task_by_id(task.id, status=next_map[task.status])  # type: ignore[attr-defined]
        self.refresh_tasks()

    def action_new_task(self) -> None:
        from taskinder.tui.screens.edit_screen import EditScreen
        self.app.push_screen(EditScreen(), self._after_edit)

    def action_edit_task(self) -> None:
        task = self._selected_task()
        if not task:
            self.app.notify("Nenhuma tarefa selecionada.", severity="warning")
            return
        from taskinder.tui.screens.edit_screen import EditScreen
        self.app.push_screen(EditScreen(task=task), self._after_edit)

    def _after_edit(self, saved: bool) -> None:
        if saved:
            self.refresh_tasks()

    def action_delete_task(self) -> None:
        task = self._selected_task()
        if not task:
            self.app.notify("Nenhuma tarefa selecionada.", severity="warning")
            return
        self.app.service.delete_task_by_id(task.id)  # type: ignore[attr-defined]
        self.app.notify(f"Tarefa deletada: {task.title[:40]}", severity="warning")
        self.refresh_tasks()

    def action_scan_todos(self) -> None:
        from taskinder.tui.screens.todo_screen import TodoScreen
        project_dir = self.app.project_dir  # type: ignore[attr-defined]
        self.app.push_screen(TodoScreen(project_dir))

    def action_switch_theme(self) -> None:
        from taskinder.tui.screens.theme_screen import ThemeScreen
        self.app.push_screen(ThemeScreen())

    def action_filter_tab(self, tab_id: str) -> None:
        self.query_one(TabbedContent).active = tab_id

    def action_show_help(self) -> None:
        help_text = (
            "j/k / ↑↓  → Navegar\n"
            "space/enter → Toggle status\n"
            "n           → Nova tarefa\n"
            "e           → Editar tarefa\n"
            "d           → Deletar tarefa\n"
            "t           → Scan TODOs\n"
            "T           → Trocar tema\n"
            "1-4         → Filtrar por aba\n"
            "q           → Sair"
        )
        self.app.notify(help_text, title="Atalhos", timeout=8)
