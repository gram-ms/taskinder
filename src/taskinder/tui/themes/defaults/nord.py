from textual.theme import Theme

NORD = Theme(
    name="nord",
    dark=True,
    primary="#88c0d0",
    secondary="#81a1c1",
    warning="#ebcb8b",
    error="#bf616a",
    success="#a3be8c",
    accent="#b48ead",
    foreground="#eceff4",
    background="#2e3440",
    surface="#3b4252",
    panel="#434c5e",
    variables={
        "input-cursor-foreground": "#2e3440",
        "input-cursor-background": "#88c0d0",
        "block-cursor-foreground": "#2e3440",
        "block-cursor-background": "#88c0d0",
    },
)
