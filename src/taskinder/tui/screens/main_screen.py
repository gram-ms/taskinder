from __future__ import annotations

from pathlib import Path

from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Horizontal, Vertical
from textual.screen import Screen
from textual.widgets import Footer, Label, Static, TabbedContent, TabPane

from taskinder.models.task import Task, TaskStatus
from taskinder.tui.widgets.task_item import TaskItem, TaskListView


class ProjectHeader(Static):
    DEFAULT_CSS = """
    ProjectHeader {
        height: 5;
        background: $panel;
        border-bottom: heavy $primary;
        layout: vertical;
        padding: 0 3;
    }
    #header-brand {
        color: $primary;
        text-style: bold;
        margin-top: 1;
    }
    #header-path {
        color: $text-muted;
        text-style: dim;
    }
    #header-stats {
        color: $foreground;
        margin-top: 0;
    }
    .stat-todo   { color: $warning; }
    .stat-doing  { color: $secondary; }
    .stat-done   { color: $success; }
    .stat-sep    { color: $text-muted; }
    """

    def compose(self) -> ComposeResult:
        cwd = Path.cwd()
        try:
            display = "~/" + str(cwd.relative_to(Path.home()))
        except ValueError:
            display = str(cwd)

        with Vertical():
            yield Label("  Taskinder", id="header-brand")
            yield Label(f"  {display}", id="header-path")
            yield Label("  loading…", id="header-stats")

    def update_counts(self, counts: dict[str, int]) -> None:
        todo  = counts.get("TODO", 0)
        doing = counts.get("DOING", 0)
        done  = counts.get("DONE", 0)
        self.query_one("#header-stats", Label).update(
            f"  [bold yellow]󰄱[/bold yellow]  {todo} "
            f"[dim]·[/dim]  [bold blue]󰑓[/bold blue]  {doing} "
            f"[dim]·[/dim]  [bold green]󰄲[/bold green]  {done}"
        )


class MainScreen(Screen):
    BINDINGS = [
        Binding("j",     "cursor_down",        "Down",   show=False),
        Binding("k",     "cursor_up",           "Up",     show=False),
        Binding("down",  "cursor_down",         show=False),
        Binding("up",    "cursor_up",           show=False),
        Binding("h",     "prev_tab",            "←",      show=False),
        Binding("l",     "next_tab",            "→",      show=False),
        Binding("n",     "new_task",            "New"),
        Binding("e",     "edit_task",           "Edit"),
        Binding("d",     "delete_task",         "Delete"),
        Binding("space", "toggle_status",       "Toggle"),
        Binding("enter", "toggle_status",       show=False),
        Binding("t",     "scan_todos",          "TODOs"),
        Binding("T",     "switch_theme",        "Theme"),
        Binding("q",     "app.quit",            "Quit"),
        Binding("question_mark", "show_help",   show=False),
        Binding("1",     "filter_tab('all')",   show=False),
        Binding("2",     "filter_tab('todo')",  show=False),
        Binding("3",     "filter_tab('doing')", show=False),
        Binding("4",     "filter_tab('done')",  show=False),
    ]

    DEFAULT_CSS = """
    MainScreen {
        background: $background;
        layout: vertical;
    }

    /* ── tabs ──────────────────────────────────── */
    TabbedContent {
        height: 1fr;
    }
    TabPane {
        padding: 0;
        background: $background;
    }

    /* ── list ──────────────────────────────────── */
    TaskListView {
        background: $background;
        height: 1fr;
        scrollbar-background: $surface;
        scrollbar-color: $primary;
        scrollbar-color-hover: $accent;
    }
    TaskItem {
        height: auto;
        padding: 0 1;
        border-left: blank $background;
    }
    TaskItem:hover {
        background: $surface;
        border-left: thick $panel;
    }
    TaskItem.--highlight {
        background: $surface;
        border-left: thick $primary;
    }

    /* ── task item internals ────────────────────── */
    .item-body {
        width: 1fr;
        height: auto;
        padding: 1 0;
    }
    .item-row-main {
        height: 1;
        width: 1fr;
    }
    .item-row-desc {
        height: 1;
        width: 1fr;
    }
    .task-icon {
        width: 3;
        text-style: bold;
    }
    .task-icon-spacer {
        width: 3;
    }
    TaskItem.todo  .task-icon { color: $warning; }
    TaskItem.doing .task-icon { color: $secondary; }
    TaskItem.done  .task-icon { color: $success; }

    .task-title {
        width: 1fr;
        color: $foreground;
    }
    TaskItem.done .task-title {
        color: $text-muted;
        text-style: dim strike;
    }
    .task-desc {
        width: 1fr;
        color: $text-muted;
        text-style: dim;
    }
    .task-time {
        width: 8;
        text-align: right;
        color: $text-muted;
        text-style: dim;
    }
    """

    def compose(self) -> ComposeResult:
        yield ProjectHeader()
        with TabbedContent(initial="all"):
            with TabPane("󰈚  All",    id="all"):
                yield TaskListView(id="list-all")
            with TabPane("󰄱  Todo",   id="todo"):
                yield TaskListView(id="list-todo")
            with TabPane("󰑓  Doing",  id="doing"):
                yield TaskListView(id="list-doing")
            with TabPane("󰄲  Done",   id="done"):
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
            return item.data
        return None

    def refresh_tasks(self) -> None:
        service = self.app.service       # type: ignore[attr-defined]
        repo    = self.app.repository    # type: ignore[attr-defined]
        tasks   = service.get_all_tasks()
        counts  = repo.count()
        self.query_one(ProjectHeader).update_counts(counts)

        groups: dict[str, list[Task]] = {
            "all":   tasks,
            "todo":  [t for t in tasks if t.status == TaskStatus.TODO],
            "doing": [t for t in tasks if t.status == TaskStatus.DOING],
            "done":  [t for t in tasks if t.status == TaskStatus.DONE],
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

    def action_prev_tab(self) -> None:
        tabs = ["all", "todo", "doing", "done"]
        tc = self.query_one(TabbedContent)
        idx = tabs.index(tc.active) if tc.active in tabs else 0
        tc.active = tabs[(idx - 1) % len(tabs)]

    def action_next_tab(self) -> None:
        tabs = ["all", "todo", "doing", "done"]
        tc = self.query_one(TabbedContent)
        idx = tabs.index(tc.active) if tc.active in tabs else 0
        tc.active = tabs[(idx + 1) % len(tabs)]

    def action_toggle_status(self) -> None:
        task = self._selected_task()
        if not task:
            return
        cycle = {
            TaskStatus.TODO:  TaskStatus.DOING,
            TaskStatus.DOING: TaskStatus.DONE,
            TaskStatus.DONE:  TaskStatus.TODO,
        }
        self.app.service.update_task_by_id(task.id, status=cycle[task.status])  # type: ignore[attr-defined]
        self.refresh_tasks()

    def action_new_task(self) -> None:
        from taskinder.tui.screens.edit_screen import EditScreen
        self.app.push_screen(EditScreen(), self._after_edit)

    def action_edit_task(self) -> None:
        task = self._selected_task()
        if not task:
            self.app.notify("No task selected.", severity="warning")
            return
        from taskinder.tui.screens.edit_screen import EditScreen
        self.app.push_screen(EditScreen(task=task), self._after_edit)

    def _after_edit(self, saved: bool) -> None:
        if saved:
            self.refresh_tasks()

    def action_delete_task(self) -> None:
        task = self._selected_task()
        if not task:
            self.app.notify("No task selected.", severity="warning")
            return
        self.app.service.delete_task_by_id(task.id)  # type: ignore[attr-defined]
        self.app.notify(f"Deleted: {task.title[:40]}", severity="warning")
        self.refresh_tasks()

    def action_scan_todos(self) -> None:
        from taskinder.tui.screens.todo_screen import TodoScreen
        self.app.push_screen(TodoScreen(self.app.project_dir))  # type: ignore[attr-defined]

    def action_switch_theme(self) -> None:
        from taskinder.tui.screens.theme_screen import ThemeScreen
        self.app.push_screen(ThemeScreen())

    def action_filter_tab(self, tab_id: str) -> None:
        self.query_one(TabbedContent).active = tab_id

    def action_show_help(self) -> None:
        self.app.notify(
            "j/k ↑↓  navigate  ·  h/l ←→  switch tab\n"
            "space   toggle status     n  new task\n"
            "e       edit task         d  delete\n"
            "t       scan TODOs        T  theme\n"
            "1-4     jump to tab       q  quit",
            title="  Keybindings",
            timeout=8,
        )
