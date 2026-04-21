from textual.theme import Theme

TOKYO_NIGHT = Theme(
    name="tokyo-night",
    dark=True,
    primary="#7aa2f7",
    secondary="#9d7cd8",
    warning="#e0af68",
    error="#f7768e",
    success="#9ece6a",
    accent="#bb9af7",
    foreground="#c0caf5",
    background="#1a1b26",
    surface="#24283b",
    panel="#2f3549",
    variables={
        "input-cursor-foreground": "#1a1b26",
        "input-cursor-background": "#7aa2f7",
        "block-cursor-foreground": "#1a1b26",
        "block-cursor-background": "#7aa2f7",
    },
)
