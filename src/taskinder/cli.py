from __future__ import annotations

import json
from pathlib import Path
from typing import Optional

import typer
from rich import box
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from taskinder.core import TaskService
from taskinder.models.task import TaskStatus
from taskinder.storage.task_repository import TaskRepository

app = typer.Typer(
    name="taskinder",
    help="Taskinder — per-project task manager (TUI + CLI)",
    invoke_without_command=True,
    no_args_is_help=False,
)
theme_app = typer.Typer(help="Manage themes")
app.add_typer(theme_app, name="theme")

console = Console()


def _get_service(cwd: Path | None = None) -> tuple[TaskService, TaskRepository]:
    project_dir = cwd or Path.cwd()
    db_path = project_dir / ".taskinder" / "tasks.db"
    repo = TaskRepository(db_path)
    return TaskService(repo), repo


def _resolve_task(task_id: str, service: TaskService, repo: TaskRepository):
    task = repo.find_by_id(task_id)
    if task:
        return task
    all_tasks = service.get_all_tasks()
    matches = [t for t in all_tasks if t.id.startswith(task_id)]
    if len(matches) == 1:
        return matches[0]
    if len(matches) > 1:
        console.print(f"[red]Ambiguous ID '{task_id}' — be more specific.[/red]")
        raise typer.Exit(1)
    console.print(f"[red]Task not found: {task_id}[/red]")
    raise typer.Exit(1)


@app.callback()
def main_callback(ctx: typer.Context) -> None:
    if ctx.invoked_subcommand is None:
        from taskinder.tui.app import TaskinderApp
        TaskinderApp().run()


@app.command()
def summary(
    dir: Optional[Path] = typer.Option(None, "--dir", "-D", help="Project directory"),
) -> None:
    """Print a FastFetch-style task summary (great for .zshrc)."""
    project_dir = dir or Path.cwd()
    service, repo = _get_service(project_dir)

    try:
        display = "~/" + str(project_dir.relative_to(Path.home()))
    except ValueError:
        display = str(project_dir)

    counts = repo.count()
    tasks = service.get_all_tasks()

    if not tasks:
        console.print(Panel(
            f"[bold]  Taskinder[/bold]  [dim]{display}[/dim]\n"
            "[dim]No tasks yet. Run [/dim][bold]taskinder add \"your task\"[/bold]",
            border_style="dim",
        ))
        return

    todo = counts.get("TODO", 0)
    doing = counts.get("DOING", 0)
    done = counts.get("DONE", 0)

    lines = [
        f"[bold]  Taskinder[/bold]  [dim]{display}[/dim]",
        f"[yellow]󰄱[/yellow] {todo} todo  [blue]󰑓[/blue] {doing} in progress  [green]󰄲[/green] {done} done",
        "",
    ]
    pending = [t for t in tasks if t.status != TaskStatus.DONE][:5]
    for task in pending:
        color = "yellow" if task.status == TaskStatus.TODO else "blue"
        icon = "󰄱" if task.status == TaskStatus.TODO else "󰑓"
        lines.append(f"  [{color}]{icon}[/{color}]  {task.title}")
    if len(pending) == 5:
        remaining = sum(1 for t in tasks if t.status != TaskStatus.DONE) - 5
        if remaining > 0:
            lines.append(f"  [dim]... and {remaining} more[/dim]")

    console.print(Panel("\n".join(lines), border_style="bright_black"))


@app.command(name="add")
def add_task(
    title: str = typer.Argument(..., help="Task title"),
    description: str = typer.Option("", "--desc", "-d", help="Task description"),
    status: str = typer.Option("TODO", "--status", "-s", help="Status: TODO, DOING, DONE"),
) -> None:
    """Add a new task to the current project."""
    service, _ = _get_service()
    try:
        s = TaskStatus(status.upper())
    except ValueError:
        console.print(f"[red]Invalid status: {status}. Use TODO, DOING or DONE.[/red]")
        raise typer.Exit(1)

    task = service.create_task(title, description)
    if s != TaskStatus.TODO:
        service.update_task_by_id(task.id, status=s)
    console.print(f"[green]✓[/green] Created: [bold]{title}[/bold]  [dim]({task.id[:8]})[/dim]")


@app.command(name="list")
def list_tasks(
    status: Optional[str] = typer.Option(None, "--status", "-s", help="Filter by status"),
    as_json: bool = typer.Option(False, "--json", help="Output as JSON"),
) -> None:
    """List tasks in the current project."""
    service, _ = _get_service()

    if status:
        try:
            s = TaskStatus(status.upper())
            tasks = service.get_task_by_status(s)
        except ValueError:
            console.print(f"[red]Invalid status: {status}[/red]")
            raise typer.Exit(1)
    else:
        tasks = service.get_all_tasks()

    if as_json:
        print(json.dumps([t.to_dict() for t in tasks], indent=2, default=str))
        return

    if not tasks:
        console.print("[dim]No tasks found.[/dim]")
        return

    icons = {TaskStatus.TODO: "○", TaskStatus.DOING: "◑", TaskStatus.DONE: "●"}
    colors = {TaskStatus.TODO: "yellow", TaskStatus.DOING: "blue", TaskStatus.DONE: "green"}

    table = Table(box=box.ROUNDED, show_header=True, header_style="bold")
    table.add_column("ID", style="dim", width=10)
    table.add_column("Status", width=14)
    table.add_column("Title")
    table.add_column("Description", style="dim")

    for task in tasks:
        icon = icons[task.status]
        color = colors[task.status]
        table.add_row(
            task.id[:8],
            f"[{color}]{icon}  {task.status.value}[/{color}]",
            task.title,
            task.description[:50] if task.description else "",
        )

    console.print(table)


@app.command(name="done")
def mark_done(task_id: str = typer.Argument(..., help="Task ID or prefix")) -> None:
    """Mark a task as done."""
    service, repo = _get_service()
    task = _resolve_task(task_id, service, repo)
    service.update_task_by_id(task.id, status=TaskStatus.DONE)
    console.print(f"[green]✓[/green] Done: [bold]{task.title}[/bold]")


@app.command(name="delete")
def delete_task(
    task_id: str = typer.Argument(..., help="Task ID or prefix"),
    yes: bool = typer.Option(False, "--yes", "-y", help="Skip confirmation prompt"),
) -> None:
    """Delete a task."""
    service, repo = _get_service()
    task = _resolve_task(task_id, service, repo)
    if not yes and not typer.confirm(f"Delete '{task.title}'?"):
        return
    service.delete_task_by_id(task.id)
    console.print(f"[red]✗[/red] Deleted: [bold]{task.title}[/bold]")


@app.command(name="edit")
def edit_task(
    task_id: str = typer.Argument(..., help="Task ID or prefix"),
    title: Optional[str] = typer.Option(None, "--title", "-t"),
    description: Optional[str] = typer.Option(None, "--desc", "-d"),
    status: Optional[str] = typer.Option(None, "--status", "-s"),
) -> None:
    """Edit a task's fields via CLI."""
    service, repo = _get_service()
    task = _resolve_task(task_id, service, repo)

    s = None
    if status:
        try:
            s = TaskStatus(status.upper())
        except ValueError:
            console.print(f"[red]Invalid status: {status}[/red]")
            raise typer.Exit(1)

    service.update_task_by_id(task.id, title=title, description=description, status=s)
    console.print(f"[green]✓[/green] Updated: [bold]{task.title}[/bold]")


@app.command(name="scan")
def scan_todos(
    dir: Optional[Path] = typer.Option(None, "--dir", "-D", help="Directory to scan"),
    import_all: bool = typer.Option(False, "--import", "-i", help="Import all as tasks"),
) -> None:
    """Scan source files for TODO/FIXME/HACK/NOTE comments."""
    from taskinder.scanner.todo_scanner import TodoScanner

    project_dir = dir or Path.cwd()
    scanner = TodoScanner()
    items = scanner.scan(project_dir)

    if not items:
        console.print("[dim]No TODOs found.[/dim]")
        return

    kind_colors = {"TODO": "blue", "FIXME": "red", "HACK": "yellow", "NOTE": "green", "XXX": "magenta"}

    table = Table(box=box.ROUNDED, title=f"{len(items)} item(s) found", header_style="bold")
    table.add_column("Kind", width=7)
    table.add_column("File", style="dim")
    table.add_column("Line", justify="right", style="dim", width=6)
    table.add_column("Text")

    for item in items:
        color = kind_colors.get(item.kind, "white")
        table.add_row(f"[{color}]{item.kind}[/{color}]", item.file, str(item.line), item.text)

    console.print(table)

    if import_all:
        service, _ = _get_service(project_dir)
        for item in items:
            service.create_task(f"{item.kind}: {item.text}", f"From {item.file}:{item.line}")
        console.print(f"[green]✓[/green] Imported {len(items)} item(s) as tasks.")


@theme_app.command(name="list")
def theme_list() -> None:
    """List available themes."""
    from taskinder.tui.themes.manager import ThemeManager

    mgr = ThemeManager()
    active = mgr.get_active_theme_name()
    for name in mgr.list_themes():
        marker = "  [green]●[/green] [dim](active)[/dim]" if name == active else ""
        console.print(f"  {name}{marker}")


@theme_app.command(name="set")
def theme_set(name: str = typer.Argument(..., help="Theme name")) -> None:
    """Set the active theme."""
    from taskinder.tui.themes.manager import ThemeManager

    mgr = ThemeManager()
    try:
        mgr.set_active_theme(name)
        console.print(f"[green]✓[/green] Theme set to: [bold]{name}[/bold]")
    except ValueError as e:
        console.print(f"[red]{e}[/red]")
        raise typer.Exit(1)


@theme_app.command(name="add")
def theme_add(
    name: str = typer.Argument(..., help="Name for the new theme"),
    file: Path = typer.Option(..., "--file", "-f", help="JSON theme file"),
) -> None:
    """Add a custom theme from a JSON file."""
    from taskinder.tui.themes.manager import ThemeManager

    mgr = ThemeManager()
    try:
        data = json.loads(file.read_text())
        mgr.add_user_theme(name, data)
        console.print(f"[green]✓[/green] Theme added: [bold]{name}[/bold]")
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        raise typer.Exit(1)


@theme_app.command(name="remove")
def theme_remove(name: str = typer.Argument(..., help="Theme name")) -> None:
    """Remove a user-defined theme."""
    from taskinder.tui.themes.manager import ThemeManager

    mgr = ThemeManager()
    try:
        mgr.remove_user_theme(name)
        console.print(f"[green]✓[/green] Theme removed: [bold]{name}[/bold]")
    except ValueError as e:
        console.print(f"[red]{e}[/red]")
        raise typer.Exit(1)


@theme_app.command(name="export")
def theme_export(name: str = typer.Argument(..., help="Theme name")) -> None:
    """Export a theme as JSON (useful for creating variants)."""
    from taskinder.tui.themes.manager import ThemeManager

    mgr = ThemeManager()
    try:
        data = mgr.export_theme(name)
        print(json.dumps(data, indent=2))
    except ValueError as e:
        console.print(f"[red]{e}[/red]")
        raise typer.Exit(1)
