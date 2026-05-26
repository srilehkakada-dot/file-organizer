import threading
import tkinter as tk
from tkinter import filedialog, ttk, scrolledtext
from pathlib import Path
from file_organizer import organize, CATEGORIES


class FileOrganizerApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("File Organizer")
        self.resizable(False, False)
        self.configure(bg="#f9f9f7")
        self._build_ui()

    def _build_ui(self):
        pad = dict(padx=16, pady=8)
        style = ttk.Style(self)
        style.configure("TButton", font=("Helvetica", 11))
        style.configure("TCheckbutton", background="#f9f9f7")
        style.configure("TLabel", background="#f9f9f7", font=("Helvetica", 11))
        style.configure("Title.TLabel", font=("Helvetica", 15, "bold"))

        ttk.Label(self, text="File Organizer", style="Title.TLabel").grid(
            row=0, column=0, columnspan=3, **pad, sticky="w"
        )

        ttk.Label(self, text="Directory:").grid(row=1, column=0, padx=16, sticky="w")
        self.dir_var = tk.StringVar()
        ttk.Entry(self, textvariable=self.dir_var, width=44).grid(
            row=1, column=1, pady=6
        )
        ttk.Button(self, text="Browse…", command=self._browse).grid(
            row=1, column=2, padx=(6, 16)
        )

        cat_frame = ttk.LabelFrame(self, text=" Categories ", padding=8)
        cat_frame.grid(row=2, column=0, columnspan=3, padx=16, pady=6, sticky="ew")
        self.cat_vars: dict[str, tk.BooleanVar] = {}
        cats = list(CATEGORIES.keys())
        for i, cat in enumerate(cats):
            v = tk.BooleanVar(value=True)
            self.cat_vars[cat] = v
            cb = ttk.Checkbutton(cat_frame, text=cat, variable=v)
            cb.grid(row=i // 4, column=i % 4, sticky="w", padx=8, pady=2)

        opt_frame = ttk.LabelFrame(self, text=" Options ", padding=8)
        opt_frame.grid(row=3, column=0, columnspan=3, padx=16, pady=6, sticky="ew")
        self.preview_var = tk.BooleanVar(value=True)
        self.skip_dup_var = tk.BooleanVar(value=True)
        self.rename_var = tk.BooleanVar(value=False)
        self.recurse_var = tk.BooleanVar(value=False)
        for i, (text, var) in enumerate([
            ("Preview only (dry run)", self.preview_var),
            ("Skip duplicates", self.skip_dup_var),
            ("Auto-rename conflicts", self.rename_var),
            ("Recurse subfolders", self.recurse_var),
        ]):
            ttk.Checkbutton(opt_frame, text=text, variable=var).grid(
                row=0, column=i, sticky="w", padx=8
            )

        self.log = scrolledtext.ScrolledText(
            self, width=68, height=14, font=("Courier", 10),
            bg="#1e1e1e", fg="#d4d4d4", insertbackground="white",
            state="disabled"
        )
        self.log.grid(row=4, column=0, columnspan=3, padx=16, pady=6)
        self.log.tag_configure("ok", foreground="#4ec9b0")
        self.log.tag_configure("err", foreground="#f48771")
        self.log.tag_configure("info", foreground="#9cdcfe")

        btn_frame = tk.Frame(self, bg="#f9f9f7")
        btn_frame.grid(row=5, column=0, columnspan=3, padx=16, pady=(4, 16))
        self.run_btn = ttk.Button(
            btn_frame, text="▶  Organize", command=self._run
        )
        self.run_btn.pack(side="left", padx=(0, 8))
        ttk.Button(btn_frame, text="Clear log", command=self._clear).pack(
            side="left"
        )
        self.status = ttk.Label(
            btn_frame, text="Ready", foreground="#888"
        )
        self.status.pack(side="left", padx=16)

    def _browse(self):
        path = filedialog.askdirectory()
        if path:
            self.dir_var.set(path)

    def _log(self, msg, tag=""):
        self.log.configure(state="normal")
        self.log.insert("end", msg + "\n", tag)
        self.log.see("end")
        self.log.configure(state="disabled")

    def _clear(self):
        self.log.configure(state="normal")
        self.log.delete("1.0", "end")
        self.log.configure(state="disabled")

    def _run(self):
        d = self.dir_var.get().strip()
        if not d:
            self._log("⚠  Please select a directory.", "err")
            return
        cats = [c for c, v in self.cat_vars.items() if v.get()]
        if not cats:
            self._log("⚠  Select at least one category.", "err")
            return
        self.run_btn.configure(state="disabled")
        self.status.configure(text="Running…")
        threading.Thread(target=self._run_thread, args=(d, cats), daemon=True).start()

    def _run_thread(self, directory, cats):
        import io, contextlib, sys

        buf = io.StringIO()
        try:
            with contextlib.redirect_stdout(buf):
                stats = organize(
                    directory=directory,
                    preview=self.preview_var.get(),
                    skip_duplicates=self.skip_dup_var.get(),
                    auto_rename=self.rename_var.get(),
                    recurse=self.recurse_var.get(),
                    categories=cats,
                )
            for line in buf.getvalue().splitlines():
                tag = "ok" if "MOVE" in line or "Done" in line else "info"
                tag = "err" if "SKIP" in line else tag
                self._log(line, tag)
            self.status.configure(
                text=f"Done — {stats.get('moved', 0)} moved, "
                     f"{stats.get('skipped', 0)} skipped"
            )
        except Exception as e:
            self._log(f"Error: {e}", "err")
            self.status.configure(text="Error")
        finally:
            self.run_btn.configure(state="normal")


if __name__ == "__main__":
    app = FileOrganizerApp()
    app.mainloop()
