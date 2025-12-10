import sys
import threading

import tkinter as tk
from tkinter import filedialog, scrolledtext

from api import flashDevice

import re

ansi_escape = re.compile(
    r'''
    \x1B    # ESC
    (?:     # 7-bit C1 Fe (except CSI)
        [@-Z\\-_]
    |       # or for CSI sequences
        \[
        [0-?]*  # Parameter bytes
        [ -/]*  # Intermediate bytes
        [@-~]   # Final byte
    )
    ''',
    re.VERBOSE
)

class StdoutRedirector:
    """Redirect 3rd party stdout to a Tkinter text widget."""
    def __init__(self, write_callback):
        self.write_callback = write_callback

    def write(self, text):
        self.write_callback(ansi_escape.sub('', text))

    def flush(self):
        pass  # not required


def cmd_in_output_window(cmd, *args, **kwargs):
    win = tk.Toplevel()
    win.title("Tool Output")
    win.geometry("800x600")

    # Expandable text box
    output_box = scrolledtext.ScrolledText(
        win, wrap=tk.WORD, font=("Consolas", 10)
    )
    output_box.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

    # --- Button Frame ---
    frame = tk.Frame(win)
    frame.pack(pady=10)

    def copy_output():
        text = output_box.get("1.0", tk.END)
        win.clipboard_clear()
        win.clipboard_append(text)

    def save_output():
        text = output_box.get("1.0", tk.END)
        path = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text Files", "*.txt"), ("All Files", "*.*")]
        )
        if path:
            with open(path, "w", encoding="utf-8") as f:
                f.write(text)

    tk.Button(frame, text="Copy", command=copy_output).pack(pady=5, padx=5, side=tk.LEFT)
    tk.Button(frame, text="Save", command=save_output).pack(pady=5, padx=5, side=tk.LEFT)
    tk.Button(frame, text="Close", command=win.destroy).pack(pady=5, padx=5, side=tk.LEFT)

    def run_tool():
        # Redirect stdout
        old_stdout = sys.stdout
        old_stderr = sys.stderr

        def append_to_output(text):
            output_box.insert(tk.END, text)
            output_box.see(tk.END)

        sys.stdout = StdoutRedirector(append_to_output)
        sys.stderr = StdoutRedirector(append_to_output)

        if 'success_callback' in kwargs:
                tk.success_callback = kwargs.pop('success_callback')
        if 'error_callback' in kwargs:
                tk.error_callback = kwargs.pop('error_callback')

        try:
            res = cmd(*args, **kwargs)
            print("Tool finished.")
            if hasattr(tk, 'success_callback'):
                tk.success_callback(res)
        except SystemExit:
            # esptool calls sys.exit() internally
            pass
        except Exception as e:
            append_to_output(f"\nERROR: {e}\n")
            if hasattr(tk, 'error_callback'):
                tk.error_callback(e)
        finally:
            sys.stdout = old_stdout
            sys.stderr = old_stderr

    threading.Thread(target=run_tool, daemon=True).start()


