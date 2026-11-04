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
    root.minsize(580, 380)
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

    # Local operator actions only: do not expose these to network customers.
    operator_controls = ttk.Frame(board_page)
    operator_controls.pack(fill="x", pady=4)
    board_name = tk.StringVar()
    ttk.Entry(operator_controls, textvariable=board_name).pack(side="left", fill="x", expand=True)

    def create_local_board():
        try:
            database.parent.mkdir(parents=True, exist_ok=True)
            BulletinBoard(database).create_board(board_name.get())
        except (OSError, ValueError, sqlite3.DatabaseError) as exc:
            messagebox.showerror("Board creation failed", str(exc))
            return
        board_name.set("")
        refresh_boards()

    ttk.Button(operator_controls, text="Create local board", command=create_local_board).pack(side="left", padx=6)

    ttk.Button(board_page, text="Refresh local boards", command=refresh_boards).pack(anchor="w")
    board_list.bind("<<ListboxSelect>>", show_posts)
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
