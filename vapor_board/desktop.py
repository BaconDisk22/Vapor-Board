"""Vapor Board local-only desktop with opt-in receive-only radio TCP."""
import sqlite3
import tkinter as tk
from tkinter import ttk
from pathlib import Path
from .config import load_shop_config
from .status import StatusSnapshot
from .tcp import TcpSettings, ConnectionState
from .radio_worker import RadioWorker
from .radio_event_state import RadioDisplayState, reduce_event
from .board_browser import BoardBrowser
from .bbs import BulletinBoard
from tkinter import messagebox


def main():
    config = load_shop_config(Path.home() / ".vapor-board" / "shop.json")
    root = tk.Tk()
    root.title(f"{config.shop_name} — Desktop")
    root.geometry("760x520")
    root.minsize(760, 520)  # smallest size where every Boards control is visible
    root.configure(bg="#15212A")

    header = tk.Frame(root, bg="#15212A", padx=24, pady=20)
    header.pack(fill="x")
    tk.Label(header, text=config.shop_name, bg="#15212A", fg="#FFFFFF",
             font=("Helvetica", 24, "bold")).pack(anchor="w")
    tk.Label(header, text="LOCAL DESKTOP • RADIO CONNECTION IS OPT-IN",
             bg="#15212A", fg="#B7D3D9", font=("Helvetica", 11)).pack(anchor="w", pady=(8, 0))

    tabs = ttk.Notebook(root)
    tabs.pack(fill="both", expand=True, padx=20, pady=12)
    for title, message in (
        ("Overview", "Connect to a Meshtastic radio explicitly from this tab."),
        ("Boards", "Local bulletin boards"),
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
    # Two columns so every control fits the default window: boards and posts
    # to pick on the left, the post view and editor on the right.
    board_column = ttk.Frame(board_page)
    board_column.pack(side="left", fill="y", padx=(0, 12))
    editor_column = ttk.Frame(board_page)
    editor_column.pack(side="left", fill="both", expand=True)
    ttk.Label(board_column, text="Local boards — local storage only").pack(anchor="w")
    board_list = tk.Listbox(board_column, height=5, width=28, exportselection=False)
    board_list.pack(fill="x", pady=4)
    posts = tk.Text(editor_column, height=5, width=30, wrap="word", state="disabled")
    posts.pack(fill="both", expand=True)
    database = Path.home() / ".vapor-board" / "bbs.sqlite"
    selected_boards = []
    shown_posts = []

    def show_posts(_event=None):
        nonlocal shown_posts
        selection = board_list.curselection()
        if not selection or selection[0] >= len(selected_boards):
            return
        try:
            shown_posts = BoardBrowser(database).posts(selected_boards[selection[0]]["id"])
            content = "\n\n".join(f'{p["author"]}: {p["body"]}' for p in shown_posts) or "No posts yet."
        except (OSError, ValueError, sqlite3.DatabaseError) as exc:
            shown_posts = []
            content = f"Unable to read local posts: {exc}"
        post_list.delete(0, "end")
        for entry in shown_posts:
            first_line = entry["body"].splitlines()[0] if entry["body"] else ""
            post_list.insert("end", f'#{entry["id"]} {entry["author"]}: {first_line[:60]}')
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

    # Local operator actions only: do not expose these to network customers.
    operator_controls = ttk.Frame(board_column)
    operator_controls.pack(fill="x")
    board_name = tk.StringVar()
    ttk.Entry(operator_controls, textvariable=board_name, width=12).pack(side="left", fill="x", expand=True)

    def create_local_board():
        try:
            database.parent.mkdir(parents=True, exist_ok=True)
            BulletinBoard(database).create_board(board_name.get())
        except (OSError, ValueError, sqlite3.DatabaseError) as exc:
            messagebox.showerror("Board creation failed", str(exc))
            return
        board_name.set("")
        refresh_boards()

    ttk.Button(operator_controls, text="Create board", command=create_local_board).pack(side="left", padx=(6, 0))
    ttk.Label(board_column, text="Select a post to edit or delete").pack(anchor="w", pady=(8, 0))
    post_list = tk.Listbox(board_column, height=5, width=28, exportselection=False)
    post_list.pack(fill="both", expand=True, pady=4)

    ttk.Label(editor_column, text="Local post author").pack(anchor="w", pady=(6, 0))
    author_name = tk.StringVar(value="Operator")
    ttk.Entry(editor_column, textvariable=author_name).pack(fill="x")
    ttk.Label(editor_column, text="Post body (local database only)").pack(anchor="w")
    post_editor = tk.Text(editor_column, height=4, width=30, wrap="word")
    post_editor.pack(fill="x")

    def save_local_post():
        selected = board_list.curselection()
        if not selected or selected[0] >= len(selected_boards):
            messagebox.showwarning("Select board", "Choose a board first.")
            return
        try:
            BulletinBoard(database).post(selected_boards[selected[0]]["id"], author_name.get(), post_editor.get("1.0", "end-1c"))
        except (ValueError, OSError, sqlite3.DatabaseError) as exc:
            messagebox.showerror("Post not saved", str(exc))
            return
        post_editor.delete("1.0", "end")
        show_posts()

    def selected_post():
        selected = post_list.curselection()
        if not selected or selected[0] >= len(shown_posts):
            messagebox.showwarning("Select post", "Choose a post first.")
            return None
        return shown_posts[selected[0]]

    def load_selected_post(_event=None):
        selected = post_list.curselection()
        if selected and selected[0] < len(shown_posts):
            post_editor.delete("1.0", "end")
            post_editor.insert("1.0", shown_posts[selected[0]]["body"])

    def update_selected_post():
        entry = selected_post()
        if entry is None:
            return
        try:
            BulletinBoard(database).edit_post(entry["id"], post_editor.get("1.0", "end-1c"))
        except (ValueError, OSError, sqlite3.DatabaseError) as exc:
            messagebox.showerror("Post not updated", str(exc))
            return
        post_editor.delete("1.0", "end")
        show_posts()

    def delete_selected_post():
        entry = selected_post()
        if entry is None:
            return
        if not messagebox.askyesno("Delete post", f'Delete post #{entry["id"]} by {entry["author"]}? This cannot be undone.'):
            return
        try:
            BulletinBoard(database).delete_post(entry["id"])
        except (ValueError, OSError, sqlite3.DatabaseError) as exc:
            messagebox.showerror("Post not deleted", str(exc))
            return
        post_editor.delete("1.0", "end")
        show_posts()

    post_actions = ttk.Frame(editor_column)
    post_actions.pack(fill="x", pady=(4, 0))
    ttk.Button(post_actions, text="Save new post", command=save_local_post).pack(side="left")
    ttk.Button(post_actions, text="Update post", command=update_selected_post).pack(side="left", padx=6)
    ttk.Button(post_actions, text="Delete post", command=delete_selected_post).pack(side="left")
    ttk.Button(board_column, text="Refresh boards", command=refresh_boards).pack(anchor="w")
    board_list.bind("<<ListboxSelect>>", show_posts)
    post_list.bind("<<ListboxSelect>>", load_selected_post)
    refresh_boards()

    # Radio connections are explicit and receive-only.
    radio_page = tabs.nametowidget(tabs.tabs()[0])
    for child in radio_page.winfo_children():
        child.destroy()
    worker = RadioWorker()
    ttk.Label(radio_page, text="Meshtastic Wi-Fi/TCP — receive only").pack(anchor="w")
    host_var = tk.StringVar(value="127.0.0.1")
    port_var = tk.StringVar(value="4403")
    ttk.Label(radio_page, text="Radio IP / host").pack(anchor="w")
    ttk.Entry(radio_page, textvariable=host_var).pack(fill="x")
    ttk.Label(radio_page, text="TCP port").pack(anchor="w")
    ttk.Entry(radio_page, textvariable=port_var).pack(fill="x")
    radio_status = tk.StringVar(value="Disconnected — no connection attempted")
    ttk.Label(radio_page, textvariable=radio_status, wraplength=550).pack(anchor="w", pady=10)
    counters = tk.StringVar(value="Decoded protobuf messages: 0")
    ttk.Label(radio_page, textvariable=counters).pack(anchor="w")
    display_state = [RadioDisplayState()]

    def connect_radio():
        try:
            settings = TcpSettings(host=host_var.get().strip(), port=int(port_var.get()), timeout=3.0)
        except (ValueError, TypeError) as exc:
            radio_status.set(f"Invalid connection settings: {exc}")
            return
        if worker.start(settings):
            display_state[0] = reduce_event(display_state[0], ('connecting', None))
            radio_status.set("Connecting to TCP; radio protocol unverified")
            update_footer()

    def disconnect_radio():
        worker.stop()
        display_state[0] = reduce_event(display_state[0], ('disconnected', None))
        radio_status.set("Disconnect requested")
        update_footer()

    controls = ttk.Frame(radio_page)
    controls.pack(anchor="w", pady=8)
    ttk.Button(controls, text="Connect", command=connect_radio).pack(side="left", padx=(0, 8))
    ttk.Button(controls, text="Disconnect", command=disconnect_radio).pack(side="left")

    def update_footer():
        footer.configure(text=StatusSnapshot(tcp_state=display_state[0].tcp, protocol_verified=display_state[0].protocol_verified).footer)

    def poll_radio():
        if not root.winfo_exists():
            return
        for _ in range(100):
            event = worker.poll()
            if event is None:
                break
            kind, data = event
            display_state[0] = reduce_event(display_state[0], event)
            counters.set(f"Decoded protobuf messages: {display_state[0].decoded}")
            radio_status.set(display_state[0].detail)
            update_footer()
        root.after(100, poll_radio)

    def on_close():
        worker.stop()
        root.destroy()

    root.protocol("WM_DELETE_WINDOW", on_close)
    footer = tk.Label(root, text=StatusSnapshot().footer,
                      bg="#15212A", fg="#FFFFFF", padx=20, pady=14, anchor="w")
    footer.pack(fill="x")
    root.after(100, poll_radio)
    root.mainloop()


if __name__ == "__main__":
    main()
