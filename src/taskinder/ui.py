from rich.table import Table
from typing import List, Dict, Any
from .models.task import Task
import rich


# Config dict of templates, move to settings later
TEMPLATES_CONFIG: Dict[str, Dict[str, Any]] = {
    "detailed": {
        "columns": ["Status", "Title", "Description", "Created At", "Updated At"],
        "style": "bold magenta",
        "show_header": True,
    },
    "default": {
        "columns": ["Status", "Title", "ID"],
        "style": "cyan",
        "border_style": "blue",
        "show_header": True,
    },
    "all": {
        "columns": ["Status", "ID", "Title", "Description", "Created At", "Updated At"],
        "style": "green",
        "show_header": True,
        "border_style": "blue",
    },
    # More later
}


# Map of columns for Obj Task
COLUMN_MAP = {
    "ID": "id",
    "Title": "title",
    "Description": "description",
    "Status": lambda v: v.status.value,
    "Created At": lambda c: c.created_at.strftime("%Y-%m-%d %H:%M"),
    "Updated At": lambda u: u.created_at.strftime("%Y-%m-%d %H:%M"),
}


def render_tasks(tasks: List[Task], template_name: str = "default"):
    """
    Renders one or more tasks in a rich table.
    This is a static utility method .
    """
    
    config = TEMPLATES_CONFIG[template_name]

    # Creates a dinamic table of the config
    table = Table(
        style=config.get("style", "default"),
        show_header=config.get("show_header", True),
        border_style=config.get("border_style", "default"),
    )

    # Add columns
    for column_name in config["columns"]:
        table.add_column(column_name)

    # Add lines
    for task in tasks:
        row_data = []
        for column_name in config["columns"]:
            mapper = COLUMN_MAP[column_name]
            if callable(mapper):
                value = mapper(task)
            else:
                value = getattr(task, mapper, "")
            row_data.append(str(value))

        table.add_row(*row_data)

    rich.print(table)
