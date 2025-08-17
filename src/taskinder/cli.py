from .models.task import Task, TaskStatus
from .storage.task_repository import TaskRepository
from .core import TaskService
from rich.table import Table
from typing import Optional, List, Union
import rich
import rich_click as click


# PARA TESTES
db = TaskRepository("db.json")

class TaskCLI:
    """Encapsulate the command logic  for the Taskinder cli"""

    def __init__(self, task_service: TaskService):
        self.task_service = task_service

    @staticmethod
    def _render_tasks(tasks: Union[Task, List[Task]]):
        """
        Renders one or more tasks in a rich table.
        This is a static utility method .
        """
        # Garants that task is list
        if not isinstance(tasks, list):
            tasks = [tasks]

        table = Table(
            "Title", "Description", "Status", "Create At", "Update at"
            )
        for task in tasks:
            table.add_row(
                task.title,
                task.description,
                task.status.value,
                task.created_at.strftime("%Y-%m-%d %H:%M"),
                task.updated_at.strftime("%Y-%m-%d %H:%M")
            )
        rich.print(table)


    def list_tasks(self, status: TaskStatus):
        """Handles the logic for listing tasks."""
        if status:
            tasks = self.task_service.get_task_by_status(status)
        else:
            tasks = self.task_service.get_all_tasks()
        
        self._render_tasks(tasks)
        


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
    help="Filter tasks by status"
    )
def list_command(ctx, status: TaskStatus):
    """Filter tasks by status"""
    ctx.obj.list_tasks(status)


    

