"""Development desktop front end. All Tk access stays on the main thread."""
import os
from pathlib import Path
import queue
import threading
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

from batch import BatchRunner
from community_support import CommunitySupport


class App:
    _COMMUNITY_REPLAY_RETRIES = 3
    _COMMUNITY_MAX_RETRY_SECONDS = 60.0

    def __init__(self, root, *, community=None, community_opener=None):
        self.root = root
        root.title("DDC IFC to Excel — development")
        root.geometry("950x570")
        root.minsize(760, 560)
        self.events = queue.Queue()
        self.runner = None
        self.worker = None
        self.closing = False
        self._destroyed = False
        self._poll_after_id = None
        self._community_after_id = None
        self.busy = False
        self.registration_window = None
        self.community = community if community is not None else CommunitySupport()
        self.community_opener = community_opener
        self.ad_requests = queue.Queue(maxsize=1)
        self.ad_stop = threading.Event()
        self.ad_worker = None
        self.files = []
        self.results = {}
        self.output = tk.StringVar(value=str(Path.home() / "Documents" / "DDC IFC to Excel"))
        self.status = tk.StringVar(value="Add .ifc or .ifczip files, choose an output folder, then convert.")
        toolbar = ttk.Frame(root, padding=10)
        toolbar.pack(fill="x")
        self.add = ttk.Button(toolbar, text="Add IFC files", command=self.add_files)
        self.add.pack(side="left")
        self.clear = ttk.Button(toolbar, text="Clear list", command=self.clear_files)
        self.clear.pack(side="left", padx=8)
        self.start = ttk.Button(toolbar, text="Convert files", command=self.run)
        self.start.pack(side="left")
        self.cancel_button = ttk.Button(toolbar, text="Cancel", command=self.cancel, state="disabled")
        self.cancel_button.pack(side="left", padx=8)
        self.registration_button = ttk.Button(toolbar, text="Registration", command=self.open_registration)
        self.registration_button.pack(side="right")
        output = ttk.Frame(root, padding=(10, 0, 10, 8))
        output.pack(fill="x")
        ttk.Label(output, text="Output folder:").pack(side="left")
        self.output_entry = ttk.Entry(output, textvariable=self.output)
        self.output_entry.pack(side="left", fill="x", expand=True, padx=8)
        self.browse = ttk.Button(output, text="Browse", command=self.choose_output)
        self.browse.pack(side="left")
        ttk.Label(root, text="Development preview: results have explicit limits. Geometry and complete fidelity are not qualified.", wraplength=920, padding=(10, 3)).pack(fill="x")
        ttk.Label(root, text="All conversion features are available. Community opens a promotional page after every two accepted conversions; Paid removes advertising.", wraplength=920, padding=(10, 0)).pack(fill="x")
        table = ttk.Frame(root)
        table.pack(fill="both", expand=True, padx=10, pady=8)
        self.tree = ttk.Treeview(table, columns=("file", "status"), show="headings", selectmode="browse")
        self.tree.heading("file", text="Source IFC")
        self.tree.heading("status", text="Status", anchor="w")
        self.tree.column("file", width=500, minwidth=200)
        self.tree.column("status", width=200, stretch=False)
        self.tree.grid(row=0, column=0, sticky="nsew")
        vertical = ttk.Scrollbar(table, orient="vertical", command=self.tree.yview)
        vertical.grid(row=0, column=1, sticky="ns")
        horizontal = ttk.Scrollbar(table, orient="horizontal", command=self.tree.xview)
        horizontal.grid(row=1, column=0, sticky="ew")
        self.tree.configure(yscrollcommand=vertical.set, xscrollcommand=horizontal.set)
        table.rowconfigure(0, weight=1)
        table.columnconfigure(0, weight=1)
        self.tree.bind("<<TreeviewSelect>>", self.show_details)
        detail_frame = ttk.Frame(root)
        detail_frame.pack(fill="x", padx=10)
        self.details = tk.Text(detail_frame, height=6, wrap="word", state="disabled")
        self.details.pack(side="left", fill="x", expand=True)
        detail_scroll = ttk.Scrollbar(detail_frame, orient="vertical", command=self.details.yview)
        detail_scroll.pack(side="right", fill="y")
        self.details.configure(yscrollcommand=detail_scroll.set)
        bottom = ttk.Frame(root, padding=10)
        bottom.pack(fill="x")
        self.open_workbook_button = ttk.Button(bottom, text="Open selected workbook", command=self.open_workbook, state="disabled")
        self.open_workbook_button.pack(side="left")
        self.open_folder_button = ttk.Button(bottom, text="Open selected result folder", command=self.open_folder, state="disabled")
        self.open_folder_button.pack(side="left", padx=8)
        self.status_label = ttk.Label(root, textvariable=self.status, wraplength=920, padding=(10, 0, 10, 10))
        self.status_label.pack(fill="x")
        # Reserve readable status/actions/details before allocating the flexible
        # table. Packing the table first lets its requested height clip status
        # text at the minimum window size or after a wrapped error message.
        self.status_label.pack_configure(side="bottom", before=table)
        bottom.pack_configure(side="bottom", before=table)
        detail_frame.pack_configure(side="bottom", before=table)
        root.bind("<Configure>", self.resize_labels, add="+")
        self.show_details()
        root.protocol("WM_DELETE_WINDOW", self.close)
        root.bind("<Destroy>", self._on_destroy, add="+")
        self._poll_after_id = root.after(100, self.poll)
        # Persisted outbox work must not depend on another conversion result.
        # Defer the DB read/launch to the background worker after UI creation.
        self._community_after_id = root.after(0, self._startup_community)

    def _cancel_after(self, attribute):
        callback = getattr(self, attribute)
        setattr(self, attribute, None)
        if callback is not None:
            try:
                self.root.after_cancel(callback)
            except tk.TclError:
                pass  # The host may already have removed this Tcl command.

    def open_registration(self):
        if self.closing or self._destroyed:
            return
        window = self.registration_window
        if window is not None and window.winfo_exists():
            window.lift()
            window.focus_set()
            return
        try:
            window = self.community.registration_dialog(self.root, language="en")
        except Exception:
            messagebox.showerror("Registration unavailable", "Registration could not be opened. All Community conversion features remain available.", parent=self.root)
            return
        self.registration_window = window

        def released(event):
            if event.widget is window and self.registration_window is window:
                self.registration_window = None
        window.bind("<Destroy>", released, add="+")

    def _startup_community(self):
        self._community_after_id = None
        self.request_community_page()

    def _on_destroy(self, event):
        if event.widget is not self.root or self._destroyed:
            return
        # A host can destroy the root without going through WM_DELETE_WINDOW.
        # Cancel only our callbacks while its Tcl interpreter is still usable.
        self._destroyed = True
        self.closing = True
        if self.registration_window is not None:
            self.registration_window.close()
        self.ad_stop.set()
        self._cancel_after("_poll_after_id")
        self._cancel_after("_community_after_id")
        if self.runner is not None:
            self.runner.cancel()

    def active(self):
        return self.worker is not None and self.worker.is_alive()

    def add_files(self):
        if self.busy or self.closing:
            return
        for name in filedialog.askopenfilenames(title="Select IFC files", filetypes=[("IFC models (*.ifc, *.ifczip)", "*.ifc *.ifczip"), ("IFC STEP", "*.ifc"), ("IFCZIP archives", "*.ifczip")]):
            if name not in self.files:
                index = len(self.files)
                self.files.append(name)
                self.tree.insert("", "end", iid=str(index), values=(name, "QUEUED"))

    def clear_files(self):
        if self.busy or self.closing:
            return
        self.tree.delete(*self.tree.get_children())
        self.files.clear()
        self.results.clear()
        self.show_details()
        self.status.set("List cleared. Add IFC files to begin.")

    def choose_output(self):
        if self.busy or self.closing:
            return
        path = filedialog.askdirectory(title="Output folder")
        if path:
            self.output.set(path)

    def run(self):
        if self.busy or self.closing:
            return
        if not self.files or not self.output.get().strip():
            messagebox.showwarning("Missing input", "Select IFC files and an output folder.")
            return
        self.results.clear()
        self.show_details()
        for i, name in enumerate(self.files):
            self.tree.item(str(i), values=(name, "QUEUED"))
        self.set_busy(True)
        try:
            results = []
            def notify(event):
                if event["event"] == "result":
                    results.append(event)
                if event["event"] != "finished":
                    self.events.put(event)
            self.runner = BatchRunner(notify, on_accepted=self.community.accepted)
            sources, output = tuple(self.files), self.output.get().strip()
            def work():
                failure = None
                try:
                    self.runner.run(sources, output)
                except Exception as exc:
                    failure = f"Conversion stopped unexpectedly: {type(exc).__name__}: {exc}"
                finally:
                    self.events.put({"event": "finished", "results": results, "failure": failure})
            self.worker = threading.Thread(target=work, daemon=False)
            self.worker.start()
        except (RuntimeError, OSError) as exc:
            self.worker = None
            self.runner = None
            self.set_busy(False)
            self.status.set("Could not start conversion. Your files remain queued; try again.")
            messagebox.showerror("Could not start conversion", str(exc), parent=self.root)

    def set_busy(self, busy):
        self.busy = busy
        for control in (self.add, self.clear, self.start, self.browse, self.output_entry):
            control.configure(state="disabled" if busy else "normal")
        self.cancel_button.configure(state="normal" if busy else "disabled")

    def cancel(self):
        if self.runner:
            self.runner.cancel()
            if self._destroyed:
                return
            self.cancel_button.configure(state="disabled")
            self.status.set("Cancelling the owned converter process; partial files will be preserved.")

    def poll(self):
        if self._destroyed:
            return
        # Tests/hosts may also pump poll explicitly. Keep one owned timer,
        # rather than leaving the previous scheduled invocation behind.
        self._cancel_after("_poll_after_id")
        try:
            while True:
                event = self.events.get_nowait()
                if event["event"] == "started":
                    self.tree.item(str(event["index"]), values=(event["source"], "RUNNING"))
                    self.status.set("Converting: " + event["source"])
                elif event["event"] == "result":
                    self.results[event["index"]] = event
                    self.tree.item(str(event["index"]), values=(event["source"], event["status"]))
                    self.show_details()
                    if event.get("community", {}).get("ad_pending") and not self.closing:
                        self.request_community_page()
                elif event["event"] == "community_page":
                    if event["status"] in ("launch_failed", "ack_lost"):
                        self.status.set("Conversion results are available. The Community page could not be opened; it will be retried later.")
                elif event["event"] == "finished":
                    self.set_busy(False)
                    results = event["results"]
                    for index, source in enumerate(self.files):
                        if index not in self.results:
                            self.results[index] = {"source": source, "status": "FAILED", "message": event.get("failure") or "Conversion ended without a result. You can retry this file."}
                            self.tree.item(str(index), values=(source, "FAILED"))
                    self.show_details()
                    written = sum(r["status"] == "CONVERTED_WITH_LIMITS" for r in results)
                    self.status.set(f"Batch ended: {written}/{len(self.files)} written with limits; {len(self.files)-written} failed, cancelled or not started.")
                    if event.get("failure"):
                        self.status.set(self.status.get() + " " + event["failure"])
        except queue.Empty:
            pass
        if self.closing and not self.active():
            self.root.destroy()
            return
        self._poll_after_id = self.root.after(100, self.poll)

    def request_community_page(self):
        if self.closing:
            return
        try:
            self.ad_requests.put_nowait(True)
        except queue.Full:
            pass  # Coalesce repeated result notifications into one replay request.
        if self.ad_worker is None or not self.ad_worker.is_alive():
            self.ad_worker = threading.Thread(target=self._open_community_pages, daemon=True)
            try:
                self.ad_worker.start()
            except (RuntimeError, OSError):
                self.ad_worker = None
                self.events.put({"event": "community_page", "status": "launch_failed"})

    def _open_community_pages(self):
        # Browser launch may block on the OS; never block Tk or the converter worker.
        while not self.closing:
            try:
                self.ad_requests.get(timeout=0.2)
            except queue.Empty:
                continue
            if self.closing:
                return
            # One queued trigger drains the persisted outbox. This avoids
            # stranding events when multiple conversions coalesce in the
            # maxsize-one wakeup queue while the OS opener is slow.
            while not self.closing:
                result = {"status": "nothing_pending"}
                for attempt in range(self._COMMUNITY_REPLAY_RETRIES + 1):
                    if self.closing:
                        return
                    try:
                        result = self.community.launch_one_pending(opener=self.community_opener)
                    except Exception:
                        result = {"status": "launch_failed"}
                    if result.get("status") != "busy_lease" or attempt >= self._COMMUNITY_REPLAY_RETRIES:
                        break
                    try:
                        delay = float(result.get("retry_after_seconds", 1.0))
                    except (TypeError, ValueError):
                        delay = 1.0
                    delay = max(0.1, min(self._COMMUNITY_MAX_RETRY_SECONDS, delay))
                    if self.ad_stop.wait(delay):
                        return
                self.events.put({"event": "community_page", **result})
                if result.get("status") != "launch_requested":
                    break

    def selected(self):
        selection = self.tree.selection()
        return self.results.get(int(selection[0])) if selection else None

    def resize_labels(self, event):
        if event.widget is self.root:
            for child in self.root.winfo_children():
                if isinstance(child, ttk.Label):
                    child.configure(wraplength=max(200, event.width - 30))

    def show_details(self, event=None):
        result = self.selected()
        text = "Select a result to inspect status and limitations."
        if result:
            text = result.get("source", "") + "\n" + result["status"] + "\n" + result["message"] + "\n" + "\n".join(result.get("limitations", []))
            if result.get("community", {}).get("warning"):
                text += "\n" + result["community"]["warning"]
        self.details.configure(state="normal")
        self.details.delete("1.0", "end")
        self.details.insert("1.0", text)
        self.details.configure(state="disabled")
        for key, button in (("workbook", self.open_workbook_button), ("folder", self.open_folder_button)):
            available = result and result["status"] == "CONVERTED_WITH_LIMITS" and result.get(key)
            button.configure(state="normal" if available else "disabled")

    def open_result(self, key):
        result = self.selected()
        if not result or result["status"] != "CONVERTED_WITH_LIMITS" or not result.get(key):
            messagebox.showinfo("No accepted result", "Select a completed result written with limits.")
            return
        try:
            os.startfile(result[key])
        except OSError as exc:
            messagebox.showerror("Cannot open result", str(exc))

    def open_workbook(self):
        self.open_result("workbook")

    def open_folder(self):
        self.open_result("folder")

    def close(self):
        if self._destroyed:
            return
        self.closing = True
        if self.registration_window is not None:
            self.registration_window.close()
        self.ad_stop.set()
        self._cancel_after("_community_after_id")
        if self.active():
            self.set_busy(True)
            self.cancel()
        else:
            self.root.destroy()


def main():
    root = tk.Tk()
    App(root)
    root.mainloop()


if __name__ == "__main__":
    main()
