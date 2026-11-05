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
from . import ui_theme as theme
from tkinter import messagebox

# Dot colour for each radio state in the sidebar and on the Overview card.
STATE_COLORS = {
    ConnectionState.DISCONNECTED: theme.MUTED,
    ConnectionState.CONNECTING: theme.WARNING,
    ConnectionState.CONNECTED: theme.SUCCESS,
    ConnectionState.ERROR: theme.DANGER,
}


def main():
    config_path = Path.home() / ".vapor-board" / "shop.json"
    config = load_shop_config(config_path)
    accent = config.accent_color
    root = tk.Tk()
    root.title(f"{config.shop_name} — Desktop")
    root.geometry("1040x680")
    root.minsize(900, 600)  # smallest size where every Boards control is visible
    fonts = theme.apply_theme(root, accent)

    # Sidebar navigation on the left, the selected page on the right.
    sidebar = ttk.Frame(root, style="Sidebar.TFrame", width=210)
    sidebar.pack(side="left", fill="y")
    sidebar.pack_propagate(False)
    tk.Frame(root, bg=theme.BORDER, width=1).pack(side="left", fill="y")
    main_area = ttk.Frame(root)
    main_area.pack(side="left", fill="both", expand=True)

    brand = ttk.Frame(sidebar, style="Sidebar.TFrame", padding=(18, 22, 18, 18))
    brand.pack(fill="x")
    tk.Frame(brand, bg=accent, width=28, height=4).pack(anchor="w", pady=(0, 10))
    ttk.Label(brand, text=config.shop_name, style="Sidebar.Brand.TLabel", wraplength=170).pack(anchor="w")
    ttk.Label(brand, text="LOCAL BULLETIN BOARD", style="Sidebar.Muted.TLabel").pack(anchor="w", pady=(2, 0))

    # Every page sits in the same grid cell and the selected one is raised.
    # Swapping with pack_forget/pack left grid-managed widgets unpainted on macOS Tk.
    page_host = ttk.Frame(main_area)
    page_host.rowconfigure(0, weight=1)
    page_host.columnconfigure(0, weight=1)
    pages = {}
    nav_buttons = {}

    def show_page(name):
        for other, button in nav_buttons.items():
            button.configure(style="NavActive.TButton" if other == name else "Nav.TButton")
        pages[name].tkraise()

    def add_page(name, title, subtitle):
        page = ttk.Frame(page_host, padding=(28, 24, 28, 16))
        page.grid(row=0, column=0, sticky="nsew")
        ttk.Label(page, text=title, style="Title.TLabel").pack(anchor="w")
        ttk.Label(page, text=subtitle, style="Muted.TLabel").pack(anchor="w", pady=(2, 18))
        pages[name] = page
        nav_buttons[name] = ttk.Button(sidebar, text=name, style="Nav.TButton", command=lambda: show_page(name))
        nav_buttons[name].pack(fill="x")
        return page

    overview_page = add_page("Overview", "Overview", "Radio connection is opt-in and receive-only.")
    board_page = add_page("Boards", "Boards", "Local bulletin boards — stored on this Mac only.")
    messages_page = add_page("Messages", "Messages", "Private messages between staff and customers.")
    customers_page = add_page("Customers", "Customers", "Customer approvals and age verification.")
    settings_page = add_page("Settings", "Settings", f"Loaded from {config_path} (read-only).")

    # Radio status pinned to the bottom of the sidebar.
    sidebar_status = ttk.Frame(sidebar, style="Sidebar.TFrame", padding=(18, 14))
    sidebar_status.pack(side="bottom", fill="x")
    ttk.Label(sidebar_status, text="RADIO", style="Sidebar.Field.TLabel").pack(anchor="w")
    status_row = ttk.Frame(sidebar_status, style="Sidebar.TFrame")
    status_row.pack(anchor="w", pady=(4, 0))
    sidebar_dot = tk.Label(status_row, text="●", bg=theme.SIDEBAR, fg=theme.MUTED, font=fonts["small"])
    sidebar_dot.pack(side="left")
    sidebar_radio = ttk.Label(status_row, text="Not connected", style="Sidebar.Muted.TLabel")
    sidebar_radio.pack(side="left", padx=(4, 0))
    ttk.Label(sidebar_status, text="Transmit disabled", style="Sidebar.Muted.TLabel").pack(anchor="w", pady=(2, 0))

    def empty_state(page, heading, body):
        inner = theme.card(page, fill="x")
        ttk.Label(inner, text=heading, style="Card.Title.TLabel").pack(anchor="w")
        ttk.Label(inner, text=body, style="Card.Muted.TLabel", wraplength=560, justify="left").pack(anchor="w", pady=(6, 0))

    empty_state(messages_page, "Private messaging is not enabled yet",
                "The inbox and message composer are on the roadmap. Messages will stay in the local database "
                "and never go out over the radio.")
    empty_state(customers_page, "Customer access is not available yet",
                "Customer approvals and 21+ age verification need a trusted operator sign-in first. "
                "Until then no customer can reach this board.")

    settings_card = theme.card(settings_page, "Shop settings", "Edit shop.json and restart to change these.", fill="x")
    settings_grid = ttk.Frame(settings_card, style="Card.TFrame")
    settings_grid.pack(fill="x", pady=(14, 0))
    for row, (label, value) in enumerate((
        ("Shop name", config.shop_name),
        ("Accent colour", config.accent_color),
        ("Notices", "On" if config.notices_enabled else "Off"),
        ("Radio transmit", "Enabled" if config.transmissions_enabled else "Disabled"),
        ("MQTT", "Enabled" if config.mqtt_enabled else "Disabled"),
        ("Customer approval", "Required" if config.customer_access_requires_approval else "Not required"),
        ("Minimum customer age", str(config.minimum_customer_age)),
    )):
        ttk.Label(settings_grid, text=label, style="Card.Muted.TLabel").grid(row=row, column=0, sticky="w", pady=5)
        ttk.Label(settings_grid, text=value, style="Card.TLabel").grid(row=row, column=1, sticky="w", padx=(32, 0), pady=5)
    tk.Frame(settings_grid, bg=accent, width=14, height=14).grid(row=1, column=2, sticky="w", padx=(10, 0))

    # Trusted local operator view only. Do not expose this to remote customers.
    # Two columns: boards and posts to pick on the left, reading pane and editor on the right.
    board_body = ttk.Frame(board_page)
    board_body.pack(fill="both", expand=True)
    board_column = ttk.Frame(board_body, width=290)
    board_column.pack(side="left", fill="y", padx=(0, 16))
    board_column.pack_propagate(False)
    editor_column = ttk.Frame(board_body)
    editor_column.pack(side="left", fill="both", expand=True)

    boards_card = theme.card(board_column, "Boards", fill="x")
    board_list = tk.Listbox(boards_card, height=5, exportselection=False)
    theme.style_list(board_list, accent, fonts["body"])
    board_list.pack(fill="x", pady=(10, 10))
    posts_card = theme.card(board_column, "Posts", "Select one to edit or delete.", fill="both", expand=True, pady=(14, 0))
    post_list = tk.Listbox(posts_card, height=5, exportselection=False)
    theme.style_list(post_list, accent, fonts["body"])
    post_list.pack(fill="both", expand=True, pady=(10, 0))

    reading_card = theme.card(editor_column, "Board", fill="both", expand=True)
    posts = tk.Text(reading_card, height=5, width=30, wrap="word", state="disabled")
    theme.style_text(posts, accent, fonts["body"])
    posts.tag_configure("author", foreground=theme.shade(accent, 1.35), font=fonts["label"])
    posts.tag_configure("meta", foreground=theme.MUTED, font=fonts["small"])
    posts.pack(fill="both", expand=True, pady=(10, 0))

    database = Path.home() / ".vapor-board" / "bbs.sqlite"
    selected_boards = []
    shown_posts = []

    def show_posts(_event=None):
        nonlocal shown_posts
        selection = board_list.curselection()
        if not selection or selection[0] >= len(selected_boards):
            return
        error = None
        try:
            shown_posts = BoardBrowser(database).posts(selected_boards[selection[0]]["id"])
        except (OSError, ValueError, sqlite3.DatabaseError) as exc:
            shown_posts = []
            error = f"Unable to read local posts: {exc}"
        posts.configure(state="normal")
        posts.delete("1.0", "end")
        for index, entry in enumerate(shown_posts):
            if index:
                posts.insert("end", "\n\n")
            posts.insert("end", entry["author"], "author")
            posts.insert("end", f'  ·  #{entry["id"]}  ·  {entry["created_at"]}\n', "meta")
            posts.insert("end", entry["body"])
        if not shown_posts:
            posts.insert("1.0", error or "No posts yet.", "meta")
        posts.configure(state="disabled")
        post_list.delete(0, "end")
        for entry in shown_posts:
            first_line = entry["body"].splitlines()[0] if entry["body"] else ""
            post_list.insert("end", f'{entry["author"]} — {first_line[:40]}')

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
        board_count.set(str(len(selected_boards)))

    # Local operator actions only: do not expose these to network customers.
    ttk.Label(boards_card, text="NEW BOARD", style="Card.Field.TLabel").pack(anchor="w", pady=(0, 4))
    operator_controls = ttk.Frame(boards_card, style="Card.TFrame")
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

    ttk.Button(operator_controls, text="Create board", style="Accent.TButton", command=create_local_board).pack(side="left", padx=(8, 0))

    composer = theme.card(editor_column, "Compose", fill="x", pady=(14, 0))
    author_row = ttk.Frame(composer, style="Card.TFrame")
    author_row.pack(fill="x", pady=(10, 6))
    ttk.Label(author_row, text="AUTHOR", style="Card.Field.TLabel").pack(side="left")
    author_name = tk.StringVar(value="Operator")
    ttk.Entry(author_row, textvariable=author_name).pack(side="left", fill="x", expand=True, padx=(12, 0))
    post_editor = tk.Text(composer, height=4, width=30, wrap="word")
    theme.style_text(post_editor, accent, fonts["body"])
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

    post_actions = ttk.Frame(composer, style="Card.TFrame")
    post_actions.pack(fill="x", pady=(12, 0))
    ttk.Button(post_actions, text="Save new post", style="Accent.TButton", command=save_local_post).pack(side="left")
    ttk.Button(post_actions, text="Update post", command=update_selected_post).pack(side="left", padx=8)
    ttk.Button(post_actions, text="Delete post", style="Danger.TButton", command=delete_selected_post).pack(side="right")
    ttk.Button(boards_card, text="Refresh boards", command=refresh_boards).pack(anchor="w", pady=(10, 0))
    board_list.bind("<<ListboxSelect>>", show_posts)
    post_list.bind("<<ListboxSelect>>", load_selected_post)

    # Radio connections are explicit and receive-only.
    radio_page = overview_page
    worker = RadioWorker()
    stats = ttk.Frame(radio_page)
    stats.pack(fill="x", pady=(0, 14))
    counters = tk.StringVar(value="0")
    board_count = tk.StringVar(value="0")
    for column, (label, variable, note) in enumerate((
        ("DECODED MESSAGES", counters, "Meshtastic protobuf frames received"),
        ("LOCAL BOARDS", board_count, "Stored in this Mac's database"),
    )):
        stat = theme.card(stats, side="left", fill="both", expand=True, padx=(0, 14) if column == 0 else 0)
        ttk.Label(stat, text=label, style="Card.Field.TLabel").pack(anchor="w")
        ttk.Label(stat, textvariable=variable, style="Card.Stat.TLabel").pack(anchor="w", pady=(4, 0))
        ttk.Label(stat, text=note, style="Card.Muted.TLabel").pack(anchor="w")

    radio_card = theme.card(radio_page, "Meshtastic Wi-Fi/TCP", "Receive only. Vapor Board never transmits.", fill="x")
    fields = ttk.Frame(radio_card, style="Card.TFrame")
    fields.pack(fill="x", pady=(14, 0))
    host_var = tk.StringVar(value="127.0.0.1")
    port_var = tk.StringVar(value="4403")
    ttk.Label(fields, text="RADIO IP / HOST", style="Card.Field.TLabel").grid(row=0, column=0, sticky="w")
    ttk.Label(fields, text="TCP PORT", style="Card.Field.TLabel").grid(row=0, column=1, sticky="w", padx=(12, 0))
    ttk.Entry(fields, textvariable=host_var).grid(row=1, column=0, sticky="ew", pady=(4, 0))
    ttk.Entry(fields, textvariable=port_var, width=8).grid(row=1, column=1, sticky="w", padx=(12, 0), pady=(4, 0))
    fields.columnconfigure(0, weight=1)
    status_line = ttk.Frame(radio_card, style="Card.TFrame")
    status_line.pack(fill="x", pady=(14, 0))
    radio_dot = tk.Label(status_line, text="●", bg=theme.CARD, fg=theme.MUTED, font=fonts["body"])
    radio_dot.pack(side="left")
    radio_status = tk.StringVar(value="Disconnected — no connection attempted")
    ttk.Label(status_line, textvariable=radio_status, style="Card.TLabel", wraplength=520).pack(side="left", padx=(6, 0))
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

    controls = ttk.Frame(radio_card, style="Card.TFrame")
    controls.pack(anchor="w", pady=(14, 0))
    ttk.Button(controls, text="Connect", style="Accent.TButton", command=connect_radio).pack(side="left", padx=(0, 8))
    ttk.Button(controls, text="Disconnect", command=disconnect_radio).pack(side="left")

    def update_footer():
        snapshot = StatusSnapshot(tcp_state=display_state[0].tcp, protocol_verified=display_state[0].protocol_verified)
        footer.configure(text=snapshot.footer)
        color = STATE_COLORS[display_state[0].tcp]
        sidebar_dot.configure(fg=color)
        radio_dot.configure(fg=color)
        sidebar_radio.configure(text=snapshot.radio_label)

    def poll_radio():
        if not root.winfo_exists():
            return
        for _ in range(100):
            event = worker.poll()
            if event is None:
                break
            kind, data = event
            display_state[0] = reduce_event(display_state[0], event)
            counters.set(str(display_state[0].decoded))
            radio_status.set(display_state[0].detail)
            update_footer()
        root.after(100, poll_radio)

    def on_close():
        worker.stop()
        root.destroy()

    root.protocol("WM_DELETE_WINDOW", on_close)
    footer = tk.Label(main_area, text=StatusSnapshot().footer, bg=theme.BACKGROUND, fg=theme.MUTED,
                      font=fonts["small"], padx=28, pady=8, anchor="w")
    footer.pack(side="bottom", fill="x")
    tk.Frame(main_area, bg=theme.BORDER, height=1).pack(side="bottom", fill="x")
    page_host.pack(fill="both", expand=True)
    refresh_boards()
    show_page("Overview")
    root.after(100, poll_radio)
    root.mainloop()


if __name__ == "__main__":
    main()
