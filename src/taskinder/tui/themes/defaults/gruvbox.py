from textual.theme import Theme

GRUVBOX = Theme(
    name="gruvbox",
    dark=True,
    primary="#d3869b",
    secondary="#83a598",
    warning="#fabd2f",
    error="#fb4934",
    success="#b8bb26",
    accent="#fe8019",
    foreground="#ebdbb2",
    background="#282828",
    surface="#3c3836",
    panel="#504945",
    variables={
        "input-cursor-foreground": "#282828",
        "input-cursor-background": "#d3869b",
        "block-cursor-foreground": "#282828",
        "block-cursor-background": "#d3869b",
    },
)
