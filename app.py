import hashlib
import os
import queue
import threading
import time
import tkinter as tk
from tkinter import ttk, messagebox
import subprocess
import sys

from services.runner import run_change_passwords
from services.csv_loader import load_ip_list
from services.state import ensure_dirs

APP_TITLE = "flora_auth — Password Changer"


def make_change_id(cur_user, cur_pass, new_user, new_pass):
    key = f"{cur_user}|{cur_pass}|{new_user}|{new_pass}"
    return hashlib.sha256(key.encode("utf-8")).hexdigest()[:16]


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title(APP_TITLE)
        self.geometry("900x600")
        self.resizable(False, False)

        ensure_dirs()

        self._build_menu()
        self._build_ui()

        self.ui_queue = queue.Queue()
        self.worker_thread = None
        self.stop_flag = threading.Event()
        self.after(100, self._drain_queue)

    # -------------------- MENU --------------------
    def _build_menu(self):
        menubar = tk.Menu(self)

        # File menu
        file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(label="Exit", command=self._on_exit)
        menubar.add_cascade(label="File", menu=file_menu)

        # Logs menu
        logs_menu = tk.Menu(menubar, tearoff=0)
        logs_menu.add_command(label="View Logs", command=self._on_view_logs)
        menubar.add_cascade(label="Logs", menu=logs_menu)

        self.config(menu=menubar)

    def _on_exit(self):
        self.destroy()

    def _on_view_logs(self):
        logs_dir = os.path.join(os.getcwd(), "logs")
        ensure_dirs()
        try:
            if not os.path.exists(logs_dir):
                os.makedirs(logs_dir, exist_ok=True)
            if sys.platform.startswith("win"):
                os.startfile(logs_dir)
            elif sys.platform == "darwin":
                subprocess.call(["open", logs_dir])
            else:
                subprocess.call(["xdg-open", logs_dir])
        except Exception as e:
            messagebox.showerror("Error", f"Could not open logs folder:\n{e}")

    # -------------------- UI --------------------
    def _build_ui(self):
        # Current credentials
        frm_current = ttk.LabelFrame(self, text="Current Credentials")
        frm_current.pack(fill="x", padx=8, pady=6)

        self.cur_user = tk.StringVar()
        self.cur_pass = tk.StringVar()

        ttk.Label(frm_current, text="Username").grid(row=0, column=0, sticky="e")
        ttk.Entry(frm_current, textvariable=self.cur_user, width=32).grid(
            row=0, column=1, sticky="w", padx=6
        )
        ttk.Label(frm_current, text="Password").grid(row=0, column=2, sticky="e")
        ttk.Entry(frm_current, textvariable=self.cur_pass, show="•", width=32).grid(
            row=0, column=3, sticky="w", padx=6
        )

        # New credentials
        frm_new = ttk.LabelFrame(self, text="New Credentials")
        frm_new.pack(fill="x", padx=8, pady=6)

        self.new_user = tk.StringVar()
        self.new_pass = tk.StringVar()
        self.new_pass2 = tk.StringVar()

        ttk.Label(frm_new, text="Username").grid(row=0, column=0, sticky="e")
        ttk.Entry(frm_new, textvariable=self.new_user, width=32).grid(
            row=0, column=1, sticky="w", padx=6
        )
        ttk.Label(frm_new, text="Password").grid(row=0, column=2, sticky="e")
        ttk.Entry(frm_new, textvariable=self.new_pass, show="•", width=32).grid(
            row=0, column=3, sticky="w", padx=6
        )
        ttk.Label(frm_new, text="Retype Password").grid(row=0, column=4, sticky="e")
        ttk.Entry(frm_new, textvariable=self.new_pass2, show="•", width=32).grid(
            row=0, column=5, sticky="w", padx=6
        )

        for i in range(6):
            frm_new.grid_columnconfigure(i, weight=0)

        # Actions
        frm_actions = ttk.Frame(self)
        frm_actions.pack(fill="x", padx=8, pady=6)

        self.btn_run = ttk.Button(
            frm_actions, text="Change Password", command=self.on_run
        )
        self.btn_run.pack(side="left")
        self.btn_stop = ttk.Button(
            frm_actions, text="Stop", command=self.on_stop, state="disabled"
        )
        self.btn_stop.pack(side="left", padx=8)
        ttk.Label(
            frm_actions, text=r"IP list CSV: .\data\device_list.csv (column A)"
        ).pack(side="right")

        # Output console
        frm_console = ttk.LabelFrame(self, text="Output")
        frm_console.pack(fill="both", expand=True, padx=8, pady=6)

        self.txt = tk.Text(frm_console, height=18, wrap="word", state="disabled")
        self.txt.pack(fill="both", expand=True, padx=6, pady=6)

    # -------------------- LOGIC --------------------
    def log(self, msg):
        self.txt.config(state="normal")
        self.txt.insert("end", f"{time.strftime('%H:%M:%S')}  {msg}\n")
        self.txt.see("end")
        self.txt.config(state="disabled")

    def on_stop(self):
        self.stop_flag.set()
        self.log("Stop requested…")

    def on_run(self):
        if self.new_pass.get() != self.new_pass2.get():
            messagebox.showerror("Validation", "New passwords do not match.")
            return
        if (
            not self.cur_user.get()
            or not self.cur_pass.get()
            or not self.new_user.get()
            or not self.new_pass.get()
        ):
            messagebox.showerror("Validation", "All fields are required.")
            return

        csv_path = os.path.join("data", "device_list.csv")
        try:
            ips = load_ip_list(csv_path)
        except Exception as e:
            messagebox.showerror("CSV Error", f"Failed to read {csv_path}\n\n{e}")
            return
        if not ips:
            messagebox.showerror("CSV Error", "No IPs found in column A.")
            return

        change_id = make_change_id(
            self.cur_user.get(),
            self.cur_pass.get(),
            self.new_user.get(),
            self.new_pass.get(),
        )
        self.log(f"Run ID: {change_id}")
        self.log(f"Devices: {len(ips)}")

        self.btn_run.config(state="disabled")
        self.btn_stop.config(state="normal")
        self.stop_flag.clear()

        args = dict(
            ips=ips,
            current_username=self.cur_user.get(),
            current_password=self.cur_pass.get(),
            new_username=self.new_user.get(),
            new_password=self.new_pass.get(),
            change_id=change_id,
            ui_queue=self.ui_queue,
            stop_flag=self.stop_flag,
        )

        self.worker_thread = threading.Thread(
            target=self._thread_run, kwargs=args, daemon=True
        )
        self.worker_thread.start()

    def _thread_run(self, **kwargs):
        try:
            run_change_passwords(**kwargs)
        except Exception as e:
            self.ui_queue.put((f"Fatal error: {e}", "ABORT"))

    def _drain_queue(self):
        try:
            while True:
                msg, level = self.ui_queue.get_nowait()
                self.log(msg)
                if level in {"DONE", "ABORT"}:
                    self.btn_run.config(state="normal")
                    self.btn_stop.config(state="disabled")
        except queue.Empty:
            pass
        self.after(150, self._drain_queue)


if __name__ == "__main__":
    app = App()
    app.mainloop()
