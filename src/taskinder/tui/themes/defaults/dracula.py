from textual.theme import Theme

DRACULA = Theme(
    name="dracula",
    dark=True,
    primary="#bd93f9",
    secondary="#8be9fd",
    warning="#ffb86c",
    error="#ff5555",
    success="#50fa7b",
    accent="#ff79c6",
    foreground="#f8f8f2",
    background="#282a36",
    surface="#44475a",
    panel="#3d3f4e",
    variables={
        "input-cursor-foreground": "#282a36",
        "input-cursor-background": "#bd93f9",
        "block-cursor-foreground": "#282a36",
        "block-cursor-background": "#bd93f9",
    },
)
