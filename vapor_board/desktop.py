"""Vapor Board local-only Tkinter desktop preview. No radio networking."""
import tkinter as tk
from tkinter import ttk
from pathlib import Path
from .config import load_shop_config


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

    footer = tk.Label(root, text="Radio: NOT CONNECTED  |  TX: DISABLED  |  MQTT: DISABLED",
                      bg="#15212A", fg="#FFFFFF", padx=20, pady=14, anchor="w")
    footer.pack(fill="x")
    root.mainloop()


if __name__ == "__main__":
    main()
