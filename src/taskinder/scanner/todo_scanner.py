import re
from dataclasses import dataclass
from pathlib import Path
from typing import List

TODO_PATTERN = re.compile(
    r"(?:#|//|/\*|--|\*|<!--)\s*(TODO|FIXME|HACK|XXX|NOTE)\b\s*:?\s*(.+?)(?:\*/|-->)?\s*$",
    re.MULTILINE,
)

EXTENSIONS = frozenset({
    ".py", ".js", ".ts", ".tsx", ".jsx", ".go", ".rs",
    ".c", ".cpp", ".h", ".hpp", ".java", ".kt", ".swift",
    ".rb", ".php", ".cs", ".lua", ".sh", ".bash", ".zsh",
    ".fish", ".r", ".scala", ".vue", ".svelte", ".html",
    ".css", ".scss", ".sass", ".toml", ".yaml", ".yml",
})

IGNORE_DIRS = frozenset({
    ".git", "__pycache__", "node_modules", ".venv", "venv",
    "dist", "build", ".taskinder", ".tox", "target",
})


@dataclass
class TodoItem:
    file: str
    line: int
    kind: str
    text: str


class TodoScanner:
    def scan(self, root: Path) -> List[TodoItem]:
        items: List[TodoItem] = []
        for path in self._walk(root):
            items.extend(self._scan_file(path, root))
        return sorted(items, key=lambda x: (x.file, x.line))

    def _walk(self, root: Path):
        for p in root.rglob("*"):
            if not p.is_file():
                continue
            if p.suffix not in EXTENSIONS:
                continue
            if any(part in IGNORE_DIRS for part in p.parts):
                continue
            yield p

    def _scan_file(self, path: Path, root: Path) -> List[TodoItem]:
        items: List[TodoItem] = []
        try:
            content = path.read_text(encoding="utf-8", errors="ignore")
            for i, line in enumerate(content.splitlines(), 1):
                m = TODO_PATTERN.search(line)
                if m:
                    items.append(TodoItem(
                        file=str(path.relative_to(root)),
                        line=i,
                        kind=m.group(1).upper(),
                        text=m.group(2).strip(),
                    ))
        except (OSError, PermissionError):
            pass
        return items
