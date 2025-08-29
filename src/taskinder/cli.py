from .models.task import TaskStatus
from .storage.task_repository import TaskRepository
from .core import TaskService
from .ui import render_tasks, TEMPLATES_CONFIG
from typing import Optional, 
import rich_click as click


# PARA TESTES
db = TaskRepository("db.json")


class TaskCLI:
    """Encapsulate the command logic  for the Taskinder cli"""

    def __init__(self, task_service: TaskService):
        self.task_service = task_service

    def list_tasks(self, status: TaskStatus, template: str):
        """Handles the logic for listing tasks."""
        if status:
            tasks = self.task_service.get_task_by_status(status)
        else:
            tasks = self.task_service.get_all_tasks()

        render_tasks(tasks, template_name=template)

    def del_task(self, id: int):
        """Delete one or more tasks by id"""
        if not self.task_service.get_task_by_id(id):
            raise click.ClickException(f"Task not found by ID: {id}")
        else:
            self.task_service.delete_task_by_id(id)

        render_tasks(self.task_service.get_all_tasks())

    def add_task(self, title: str, description: str = ""):
        """Create a new task"""
        task = self.task_service.create_task(title=title, description=description)

        render_tasks([task])

    def edit_task(self, id: int,  )


@click.group()
@click.pass_context
def cli(ctx):
    task_service = TaskService(db)
    ctx.obj = TaskCLI(task_service)


@cli.command("list")
@click.pass_context
@click.option(
    "--status",
    type=click.Choice(TaskStatus, case_sensitive=False),
    help="Filter tasks by status",
)
@click.option(
    "--template",
    type=click.Choice(list(TEMPLATES_CONFIG.keys()), case_sensitive=False),
    default="default",
    help="The display template to use for output.",
)
def list_command(ctx, status: TaskStatus, template: str):
    """Show the tasks on diretory"""
    ctx.obj.list_tasks(status, template)


@cli.command("del")
@click.argument("id", type=int)
@click.pass_context
def del_command(ctx, id: str):
    """Delete a task by id"""
    ctx.obj.del_task(id)


@cli.command("add")
@click.argument("title", type=str)
@click.option(
    "--description",
    "-d",
    type=str,
    help="The description of task")
@click.pass_context
def add_command(ctx, title: str, description: str):
    """Add a new Task"""
    print(type(description))
    ctx.obj.add_task(title=title, description=description)


