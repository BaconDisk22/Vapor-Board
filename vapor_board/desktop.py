"""Vapor Board local-only Tkinter desktop preview. No radio networking."""
import sqlite3
import tkinter as tk
from tkinter import ttk
from pathlib import Path
from .config import load_shop_config
from .status import StatusSnapshot
from .board_browser import BoardBrowser


def main():
    config = load_shop_config(Path.home() / ".vapor-board" / "shop.json")
    root = tk.Tk()
    root.title(f"{config.shop_name} — Desktop Preview")
    root.geometry("760x520")
    root.minsize(580, 380)
    root.configure(bg="#15212A")

    header = tk.Frame(root, bg="#15212A", padx=24, pady=20)
    header.pack(fill="x")
    tk.Label(header, text=config.shop_name, bg="#15212A", fg="#FFFFFF",
             font=("Helvetica", 24, "bold")).pack(anchor="w")
    tk.Label(header, text="LOCAL DESKTOP PREVIEW • NO RADIO CONNECTION",
             bg="#15212A", fg="#B7D3D9", font=("Helvetica", 11)).pack(anchor="w", pady=(8, 0))

    tabs = ttk.Notebook(root)
    tabs.pack(fill="both", expand=True, padx=20, pady=12)
    for title, message in (
        ("Overview", "Vapor Board is running locally. No radio connection has been attempted."),
        ("Boards", "Bulletin board integration is not enabled in this preview."),
        ("Messages", "Private messaging integration is not enabled in this preview."),
        ("Customers", "Customer approvals require a trusted identity provider; not available here."),
        ("Settings", "Settings are loaded from ~/.vapor-board/shop.json (read-only preview)."),
    ):
        page = ttk.Frame(tabs, padding=20)
        tabs.add(page, text=title)
        ttk.Label(page, text=message, wraplength=600).pack(anchor="w")

    # Trusted local operator view only. Do not expose this to remote customers.
    board_page = tabs.nametowidget(tabs.tabs()[1])
    for child in board_page.winfo_children():
        child.destroy()
    ttk.Label(board_page, text="Local operator board viewer (read-only)").pack(anchor="w")
    board_list = tk.Listbox(board_page, height=8, exportselection=False)
    board_list.pack(fill="x", pady=6)
    posts = tk.Text(board_page, height=10, wrap="word", state="disabled")
    posts.pack(fill="both", expand=True)
    database = Path.home() / ".vapor-board" / "bbs.sqlite"
    selected_boards = []

    def show_posts(_event=None):
        selection = board_list.curselection()
        if not selection:
            return
        try:
            entries = BoardBrowser(database).posts(selected_boards[selection[0]]["id"])
            content = "\\n\\n".join(f'{p["author"]}: {p["body"]}' for p in entries) or "No posts yet."
        except (OSError, ValueError, sqlite3.DatabaseError) as exc:
            content = f"Unable to read local posts: {exc}"
        posts.configure(state="normal")
        posts.delete("1.0", "end")
        posts.insert("1.0", content)
        posts.configure(state="disabled")

    def refresh_boards():
        nonlocal selected_boards
        board_list.delete(0, "end")
        try:
            selected_boards = BoardBrowser(database).boards()
            for board in selected_boards:
                board_list.insert("end", board["name"])
        except (OSError, ValueError, sqlite3.DatabaseError) as exc:
            selected_boards = []
            board_list.insert("end", f"Local database unavailable: {exc}")

    ttk.Button(board_page, text="Refresh local boards", command=refresh_boards).pack(anchor="w")
    board_list.bind("<<ListboxSelect>>", show_posts)
    refresh_boards()

    footer = tk.Label(root, text=StatusSnapshot().footer,
                      bg="#15212A", fg="#FFFFFF", padx=20, pady=14, anchor="w")
    footer.pack(fill="x")
    root.mainloop()


if __name__ == "__main__":
    main()
