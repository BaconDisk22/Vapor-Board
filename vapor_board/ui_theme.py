"""Desktop look and feel: one dark palette and the ttk styles built from it."""
import tkinter as tk
import tkinter.font as tkfont
from tkinter import ttk

# Surfaces from darkest (sidebar) to lightest (inputs on cards).
SIDEBAR = "#0B1117"
BACKGROUND = "#10171E"
CARD = "#161F28"
FIELD = "#0E151C"
BORDER = "#253240"
TEXT = "#E6EDF3"
MUTED = "#8B98A5"
SUCCESS = "#3FB950"
WARNING = "#D29922"
DANGER = "#F85149"


def shade(color, factor):
    """Lighten (factor > 1) or darken (factor < 1) a #RRGGBB color."""
    channels = (int(color[i:i + 2], 16) for i in (1, 3, 5))
    return "#" + "".join(f"{max(0, min(255, round(c * factor))):02X}" for c in channels)


def fonts():
    family = tkfont.nametofont("TkDefaultFont").actual("family")
    return {
        "body": (family, 13),
        "small": (family, 11),
        "label": (family, 11, "bold"),
        "nav": (family, 13),
        "title": (family, 22, "bold"),
        "card_title": (family, 14, "bold"),
        "brand": (family, 16, "bold"),
        "stat": (family, 28, "bold"),
        "mono": ("Menlo", 12),
    }


def apply_theme(root, accent):
    """Install the Vapor Board styles on root and return the font table."""
    f = fonts()
    root.configure(bg=BACKGROUND)
    style = ttk.Style(root)
    style.theme_use("clam")  # aqua ignores custom colors; clam honours them
    style.configure(".", background=BACKGROUND, foreground=TEXT, font=f["body"],
                    bordercolor=BORDER, lightcolor=BORDER, darkcolor=BORDER,
                    troughcolor=FIELD, focuscolor=accent)

    for name, bg in (("TFrame", BACKGROUND), ("Card.TFrame", CARD), ("Sidebar.TFrame", SIDEBAR)):
        style.configure(name, background=bg)
    for prefix, bg in (("", BACKGROUND), ("Card.", CARD), ("Sidebar.", SIDEBAR)):
        style.configure(f"{prefix}TLabel", background=bg, foreground=TEXT, font=f["body"])
        style.configure(f"{prefix}Muted.TLabel", background=bg, foreground=MUTED, font=f["small"])
        style.configure(f"{prefix}Field.TLabel", background=bg, foreground=MUTED, font=f["label"])
    # ttk resolves "Card.Title.TLabel" via "Title.TLabel", not "Card.TLabel", so set backgrounds here too.
    style.configure("Title.TLabel", background=BACKGROUND, font=f["title"])
    style.configure("Card.Title.TLabel", background=CARD, font=f["card_title"])
    style.configure("Card.Stat.TLabel", background=CARD, font=f["stat"])
    style.configure("Sidebar.Brand.TLabel", background=SIDEBAR, font=f["brand"])

    def button(name, bg, fg, hover, border=None):
        style.configure(name, background=bg, foreground=fg, font=f["label"], padding=(14, 7),
                        borderwidth=1, relief="flat", bordercolor=border or bg,
                        lightcolor=bg, darkcolor=bg, focuscolor=bg, anchor="center")
        style.map(name, background=[("disabled", CARD), ("pressed", shade(hover, 0.9)), ("active", hover)],
                  foreground=[("disabled", MUTED)],
                  lightcolor=[("active", hover)], darkcolor=[("active", hover)])

    button("Accent.TButton", accent, "#FFFFFF", shade(accent, 1.15))
    button("TButton", "#1F2A35", TEXT, "#283543", BORDER)
    button("Danger.TButton", "#2A1A1E", "#FF7B72", "#3A1F25", "#4A2329")

    style.configure("Nav.TButton", background=SIDEBAR, foreground=MUTED, font=f["nav"], anchor="w",
                    padding=(18, 9), borderwidth=0, relief="flat", focuscolor=SIDEBAR,
                    lightcolor=SIDEBAR, darkcolor=SIDEBAR, bordercolor=SIDEBAR)
    style.map("Nav.TButton", background=[("active", "#141C24")], foreground=[("active", TEXT)])
    style.configure("NavActive.TButton", background="#16212B", foreground=TEXT, font=f["nav"], anchor="w",
                    padding=(18, 9), borderwidth=0, relief="flat", focuscolor="#16212B",
                    lightcolor="#16212B", darkcolor="#16212B", bordercolor="#16212B")
    style.map("NavActive.TButton", background=[("active", "#16212B")])

    style.configure("TEntry", fieldbackground=FIELD, foreground=TEXT, insertcolor=TEXT, padding=(8, 6),
                    bordercolor=BORDER, lightcolor=FIELD, darkcolor=FIELD)
    style.map("TEntry", bordercolor=[("focus", accent)], lightcolor=[("focus", accent)])
    style.configure("Vertical.TScrollbar", background=CARD, troughcolor=CARD, bordercolor=CARD,
                    arrowcolor=MUTED, lightcolor=CARD, darkcolor=CARD, gripcount=0)
    return f


def card(parent, title=None, subtitle=None, **pack):
    """A bordered card frame; returns the inner frame to fill."""
    outer = tk.Frame(parent, bg=CARD, highlightthickness=1, highlightbackground=BORDER, highlightcolor=BORDER)
    outer.pack(**pack)
    inner = ttk.Frame(outer, style="Card.TFrame", padding=16)
    inner.pack(fill="both", expand=True)
    if title:
        ttk.Label(inner, text=title, style="Card.Title.TLabel").pack(anchor="w")
    if subtitle:
        ttk.Label(inner, text=subtitle, style="Card.Muted.TLabel", wraplength=520, justify="left").pack(anchor="w", pady=(2, 0))
    return inner


def style_list(widget, accent, font):
    widget.configure(bg=FIELD, fg=TEXT, font=font, relief="flat", borderwidth=0, activestyle="none",
                     highlightthickness=1, highlightbackground=BORDER, highlightcolor=accent,
                     selectbackground=shade(accent, 0.75), selectforeground="#FFFFFF")


def style_text(widget, accent, font):
    widget.configure(bg=FIELD, fg=TEXT, font=font, relief="flat", borderwidth=0, padx=10, pady=8,
                     insertbackground=TEXT, highlightthickness=1, highlightbackground=BORDER,
                     highlightcolor=accent, selectbackground=shade(accent, 0.75), spacing1=2, spacing3=2)
