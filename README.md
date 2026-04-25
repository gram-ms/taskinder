# Taskinder

A task manager that lives in your terminal and knows which project you're in.

The idea is simple: every directory gets its own tasks. Open Taskinder in a project folder and you see only what's relevant there — no noise from other repos, no shared lists. Close it, open another project, different tasks.

It runs entirely in the terminal (TUI), has a CLI for scripting and automation, and looks decent doing it.

---

## Installation

Requires Python 3.11+.

```bash
git clone https://github.com/gram-ms/taskinder
cd taskinder
python -m venv .venv
source .venv/bin/activate
pip install -e .
```

That's it. The `taskinder` command will be available inside the virtualenv.

---

## How it works

When you run `taskinder` inside a directory, it looks for (or creates) a `.taskinder/tasks.db` file right there. That SQLite file holds all tasks for that project. Nothing is shared globally unless you want it to be.

```
my-project/
├── .taskinder/
│   └── tasks.db   ← tasks live here
├── src/
└── ...
```

---

## Usage

### TUI

```bash
taskinder
```

Launches the interactive interface. Navigation works with vim keys or arrows.

| Key | Action |
|-----|--------|
| `j` / `k` | move up and down |
| `h` / `l` | switch tabs |
| `space` | cycle task status (todo → doing → done) |
| `n` | new task |
| `e` | edit selected task |
| `d` | delete selected task |
| `t` | scan project for TODO comments |
| `T` | switch theme |
| `1` `2` `3` `4` | jump to tab (All, Todo, Doing, Done) |
| `?` | show help |
| `q` | quit |

### CLI

For when you want to stay in the shell or automate things.

```bash
# add a task
taskinder add "fix the login bug" -d "happens on mobile safari" -s TODO

# list tasks
taskinder list
taskinder list --status doing
taskinder list --json

# mark done (accepts partial ID)
taskinder done a1b2c3

# edit
taskinder edit a1b2c3 --title "new title" --status DONE

# delete
taskinder delete a1b2c3

# scan source files for TODO/FIXME/HACK/NOTE
taskinder scan
taskinder scan --import        # import all found items as tasks
```

### Summary (FastFetch style)

```bash
taskinder summary
```

Prints a quick overview of the current project's tasks. Add it to your `.zshrc` or `.bashrc` to see it every time you open a terminal in that directory:

```zsh
# .zshrc
taskinder summary 2>/dev/null
```

---

## Themes

Five themes ship by default: **Catppuccin**, **Nord**, **Dracula**, **Gruvbox**, and **Tokyo Night**.

```bash
taskinder theme list
taskinder theme set nord
```

You can add your own by creating a JSON file with the color fields:

```json
{
  "name": "my-theme",
  "dark": true,
  "primary": "#your-color",
  "secondary": "#your-color",
  "background": "#your-color",
  "surface": "#your-color",
  "panel": "#your-color",
  "success": "#your-color",
  "warning": "#your-color",
  "error": "#your-color",
  "accent": "#your-color",
  "foreground": "#your-color"
}
```

```bash
taskinder theme add my-theme --file my-theme.json
taskinder theme remove my-theme
taskinder theme export catppuccin > base.json   # export any theme as a starting point
```

Themes switch instantly inside the TUI — no restart needed.

---

## TODO Scanner

Press `t` in the TUI (or run `taskinder scan`) to scan the current project for comments like `TODO`, `FIXME`, `HACK`, `NOTE`, and `XXX` across most languages. From the results you can import any item directly as a task.

Supports: `.py` `.js` `.ts` `.go` `.rs` `.java` `.c` `.cpp` `.rb` `.php` `.cs` `.lua` `.sh` `.vue` `.svelte` `.html` and more.

---

## Requirements

- Python 3.11+
- A terminal with [Nerd Fonts](https://www.nerdfonts.com/) for the icons (optional, falls back gracefully)
