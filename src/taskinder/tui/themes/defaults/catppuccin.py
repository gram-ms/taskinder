from textual.theme import Theme

CATPPUCCIN = Theme(
    name="catppuccin",
    dark=True,
    primary="#cba6f7",
    secondary="#89b4fa",
    warning="#f9e2af",
    error="#f38ba8",
    success="#a6e3a1",
    accent="#f5c2e7",
    foreground="#cdd6f4",
    background="#1e1e2e",
    surface="#313244",
    panel="#45475a",
    variables={
        "input-cursor-foreground": "#1e1e2e",
        "input-cursor-background": "#cba6f7",
        "block-cursor-foreground": "#1e1e2e",
        "block-cursor-background": "#cba6f7",
    },
)
