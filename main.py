import os
import sys
import sqlite3
import datetime
import customtkinter as ctk
from tkinter import messagebox

ctk.set_appearance_mode("light")
ctk.set_default_color_theme("blue")

# ── Path helper ───────────────────────────────────────────────────────────────
def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

DB_PATH = resource_path("solicitation_tracker.db")

# ── Color Palette (matches document tracker style) ────────────────────────────
ACCENT      = "#0038A8"   # Philippine flag blue
ACCENT_DARK = "#002d86"
SURFACE     = "#F4F6F8"
CARD        = "#FFFFFF"
BORDER      = "#D5D8DC"
TEXT_MAIN   = "#1C2833"
TEXT_SUB    = "#5D6D7E"
SUCCESS     = "#1E8449"
DANGER      = "#C0392B"
WARNING     = "#B7950B"
ROW_ALT     = "#EAF0F6"

TAB_IDLE_BG     = "#D6E4F0"
TAB_IDLE_TEXT   = ACCENT

BARANGAYS = ["Guadalupe Nuevo", "Guadalupe Viejo", "Pinagkaisahan"]
CATEGORIES = ["Medical", "Financial", "Burial", "Educational", "Others"]
STATUSES   = ["Pending", "Processing", "Ready for Pick-up"]

STATUS_COLORS = {
    "Pending":           DANGER,
    "Processing":        WARNING,
    "Ready for Pick-up": SUCCESS,
}

# ── Database ──────────────────────────────────────────────────────────────────
def init_db():
    con = sqlite3.connect(DB_PATH)
    cur = con.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS solicitations (
            id       INTEGER PRIMARY KEY AUTOINCREMENT,
            name     TEXT NOT NULL,
            barangay TEXT,
            category TEXT,
            status   TEXT DEFAULT 'Pending',
            date     TEXT,
            remarks  TEXT
        )
    """)

    con.commit()
    con.close()


def db_connect():
    return sqlite3.connect(DB_PATH)


# ── Reusable widgets ──────────────────────────────────────────────────────────
def section_label(parent, text):
    return ctk.CTkLabel(parent, text=text,
                        font=ctk.CTkFont(family="Georgia", size=12, weight="bold"),
                        text_color=ACCENT)


def divider(parent):
    f = ctk.CTkFrame(parent, fg_color=BORDER, height=1)
    f.pack(fill="x", pady=6)
    return f


# ── Log New Request Tab ───────────────────────────────────────────────────────
class LogTab(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master, fg_color=SURFACE, corner_radius=0)
        self._build()

    def _build(self):
        # Scrollable inner container
        scroll = ctk.CTkScrollableFrame(self, fg_color=SURFACE, corner_radius=0)
        scroll.pack(fill="both", expand=True, padx=30, pady=20)

        # ── Title ──
        ctk.CTkLabel(scroll, text="Log New Solicitation Request",
                     font=ctk.CTkFont(family="Georgia", size=18, weight="bold"),
                     text_color=ACCENT).pack(anchor="w", pady=(0, 4))
        divider(scroll)

        # ── Name row ──
        name_hdr = ctk.CTkFrame(scroll, fg_color="transparent")
        name_hdr.pack(fill="x", pady=(6, 2))
        section_label(name_hdr, "Resident Full Name").pack(side="left")
        self._dup_label = ctk.CTkLabel(name_hdr, text="",
                                       font=ctk.CTkFont(size=11, slant="italic"))
        self._dup_label.pack(side="right")

        self._name_var = ctk.StringVar()
        name_entry = ctk.CTkEntry(scroll, textvariable=self._name_var,
                                  placeholder_text="Enter full name…",
                                  height=36, font=ctk.CTkFont(size=13))
        name_entry.pack(fill="x", pady=(0, 12))
        name_entry.bind("<KeyRelease>", self._check_duplicate)

        # ── Dropdowns row ──
        row1 = ctk.CTkFrame(scroll, fg_color="transparent")
        row1.pack(fill="x", pady=4)

        # Barangay
        col_brgy = ctk.CTkFrame(row1, fg_color="transparent")
        col_brgy.pack(side="left", expand=True, fill="x", padx=(0, 10))
        section_label(col_brgy, "Barangay").pack(anchor="w")
        self._brgy_var = ctk.StringVar(value=BARANGAYS[0])
        ctk.CTkOptionMenu(col_brgy, variable=self._brgy_var,
                          values=BARANGAYS, height=34).pack(fill="x", pady=(4, 0))

        # Category
        col_cat = ctk.CTkFrame(row1, fg_color="transparent")
        col_cat.pack(side="left", expand=True, fill="x", padx=(0, 10))
        section_label(col_cat, "Category").pack(anchor="w")
        self._cat_var = ctk.StringVar(value=CATEGORIES[0])
        ctk.CTkOptionMenu(col_cat, variable=self._cat_var,
                          values=CATEGORIES, height=34).pack(fill="x", pady=(4, 0))

        # Status
        col_stat = ctk.CTkFrame(row1, fg_color="transparent")
        col_stat.pack(side="left", expand=True, fill="x")
        section_label(col_stat, "Status").pack(anchor="w")
        self._status_var = ctk.StringVar(value=STATUSES[0])
        ctk.CTkOptionMenu(col_stat, variable=self._status_var,
                          values=STATUSES, height=34).pack(fill="x", pady=(4, 0))

        divider(scroll)

        # ── Requirements checkboxes ──
        section_label(scroll, "Requirements Submitted").pack(anchor="w", pady=(4, 6))
        chk_row = ctk.CTkFrame(scroll, fg_color="transparent")
        chk_row.pack(fill="x", pady=(0, 10))

        self._id_var  = ctk.BooleanVar()
        self._brgy_cert_var = ctk.BooleanVar()
        self._med_var = ctk.BooleanVar()

        ctk.CTkCheckBox(chk_row, text="Valid ID",            variable=self._id_var).pack(side="left", padx=(0, 16))
        ctk.CTkCheckBox(chk_row, text="Barangay Certificate", variable=self._brgy_cert_var).pack(side="left", padx=(0, 16))
        ctk.CTkCheckBox(chk_row, text="Medical Certificate", variable=self._med_var).pack(side="left")

        divider(scroll)

        # ── Remarks ──
        section_label(scroll, "Additional Remarks (optional)").pack(anchor="w", pady=(4, 4))
        self._remarks_box = ctk.CTkTextbox(scroll, height=80,
                                           font=ctk.CTkFont(family="Courier New", size=12),
                                           border_width=1, border_color=BORDER)
        self._remarks_box.pack(fill="x", pady=(0, 14))

        # ── Buttons ──
        btn_row = ctk.CTkFrame(scroll, fg_color="transparent")
        btn_row.pack(pady=6)

        ctk.CTkButton(btn_row, text="  Save Record", width=160, height=38,
                      fg_color=ACCENT, hover_color=ACCENT_DARK,
                      font=ctk.CTkFont(size=13, weight="bold"),
                      command=self._save).pack(side="left", padx=8)

        ctk.CTkButton(btn_row, text="  Clear Form", width=140, height=38,
                      fg_color="#6c757d", hover_color="#5a6268",
                      font=ctk.CTkFont(size=13),
                      command=self._clear).pack(side="left", padx=8)

    # ── Logic ─────────────────────────────────────────────────────────────────
    def _check_duplicate(self, _event=None):
        name = self._name_var.get().upper().strip()
        if len(name) < 3:
            self._dup_label.configure(text="")
            return
        try:
            with db_connect() as con:
                row = con.execute(
                    "SELECT date, status FROM solicitations WHERE name = ? ORDER BY id DESC LIMIT 1",
                    (name,)
                ).fetchone()
            if row:
                self._dup_label.configure(
                    text=f"⚠  Existing record: {row[0]}  ({row[1]})",
                    text_color=DANGER)
            else:
                self._dup_label.configure(text="✓ New resident", text_color=SUCCESS)
        except Exception as e:
            print(f"Duplicate check error: {e}")

    def _save(self):
        name = self._name_var.get().upper().strip()
        if not name:
            messagebox.showwarning("Missing Field", "Please enter the resident's full name.")
            return

        brgy     = self._brgy_var.get()
        category = self._cat_var.get()
        status   = self._status_var.get()
        today    = datetime.date.today().strftime("%Y-%m-%d")

        reqs = []
        if self._id_var.get():       reqs.append("Valid ID")
        if self._brgy_cert_var.get(): reqs.append("Barangay Certificate")
        if self._med_var.get():       reqs.append("Medical Certificate")

        remarks_text = self._remarks_box.get("1.0", "end-1c").strip()

        parts = []
        if reqs:
            parts.append(f"Requirements submitted: {', '.join(reqs)}.")
        if remarks_text:
            parts.append(remarks_text)

        full_remarks = "  ".join(parts)

        with db_connect() as con:
            con.execute(
                "INSERT INTO solicitations (name, barangay, category, status, date, remarks) VALUES (?, ?, ?, ?, ?, ?)",
                (name, brgy, category, status, today, full_remarks)
            )
            con.commit()

        messagebox.showinfo("Saved", f"Record for {name} saved successfully.")
        self._clear()

    def _clear(self):
        self._name_var.set("")
        self._dup_label.configure(text="")
        self._brgy_var.set(BARANGAYS[0])
        self._cat_var.set(CATEGORIES[0])
        self._status_var.set(STATUSES[0])
        self._id_var.set(False)
        self._brgy_cert_var.set(False)
        self._med_var.set(False)
        self._remarks_box.delete("1.0", "end")


# ── Solicitation List Tab ─────────────────────────────────────────────────────
class ListTab(ctk.CTkFrame):
    COL_DEFS = [
        ("Name",     220, "w"),
        ("Barangay", 150, "center"),
        ("Category", 120, "center"),
        ("Status",   150, "center"),
        ("Date",     100, "center"),
        ("Remarks",  260, "w"),
        ("Actions",  110, "center"),
    ]

    def __init__(self, master):
        super().__init__(master, fg_color=SURFACE, corner_radius=0)
        self._sort = "id DESC"
        self._build()

    def _build(self):
        # ── Top bar ──
        top = ctk.CTkFrame(self, fg_color=SURFACE, corner_radius=0)
        top.pack(fill="x", padx=20, pady=(16, 4))

        ctk.CTkLabel(top, text="Solicitation Records",
                     font=ctk.CTkFont(family="Georgia", size=17, weight="bold"),
                     text_color=ACCENT).pack(side="left")

        self._search_var = ctk.StringVar()
        search = ctk.CTkEntry(top, textvariable=self._search_var,
                              placeholder_text="Search name…",
                              width=280, height=32)
        search.pack(side="right", padx=(0, 6))
        search.bind("<KeyRelease>", lambda _e: self._load())

        # Status filter
        self._filter_var = ctk.StringVar(value="All")
        ctk.CTkOptionMenu(top, variable=self._filter_var,
                          values=["All"] + STATUSES,
                          width=160, height=32,
                          command=lambda _v: self._load()).pack(side="right", padx=6)

        # ── Column headers ──
        hdr = ctk.CTkFrame(self, fg_color="gray25", corner_radius=0, height=34)
        hdr.pack(fill="x", padx=20)
        hdr.pack_propagate(False)

        sort_map = {
            "Name":     "name ASC",
            "Barangay": "barangay ASC",
            "Category": "category ASC",
            "Status":   "status ASC",
            "Date":     "id DESC",
        }
        for col, width, _ in self.COL_DEFS:
            if col in sort_map:
                btn = ctk.CTkButton(
                    hdr, text=col, width=width, height=34,
                    fg_color="transparent", hover_color="gray35",
                    text_color="white",
                    font=ctk.CTkFont(size=12, weight="bold"),
                    corner_radius=0,
                    command=lambda s=sort_map[col]: self._set_sort(s)
                )
                btn.pack(side="left")
            else:
                ctk.CTkLabel(hdr, text=col, width=width,
                             text_color="white",
                             font=ctk.CTkFont(size=12, weight="bold")).pack(side="left")

        # ── Scrollable rows ──
        self._rows_frame = ctk.CTkScrollableFrame(
            self, fg_color=SURFACE, corner_radius=0)
        self._rows_frame.pack(fill="both", expand=True, padx=20, pady=(0, 10))

        self._load()

    def _set_sort(self, sql):
        self._sort = sql
        self._load()

    def _load(self):
        for w in self._rows_frame.winfo_children():
            w.destroy()

        search = self._search_var.get().upper()
        filt   = self._filter_var.get()

        query = "SELECT id, name, barangay, category, status, date, remarks FROM solicitations WHERE name LIKE ?"
        params = [f"%{search}%"]

        if filt != "All":
            query += " AND status = ?"
            params.append(filt)

        query += f" ORDER BY {self._sort}"

        with db_connect() as con:
            rows = con.execute(query, params).fetchall()

        if not rows:
            ctk.CTkLabel(self._rows_frame, text="No records found.",
                         text_color=TEXT_SUB,
                         font=ctk.CTkFont(size=13, slant="italic")).pack(pady=30)
            return

        for i, (rid, name, brgy, cat, status, date, remarks) in enumerate(rows):
            bg = CARD if i % 2 == 0 else ROW_ALT
            row_f = ctk.CTkFrame(self._rows_frame, fg_color=bg,
                                 corner_radius=4, height=34)
            row_f.pack(fill="x", pady=1)
            row_f.pack_propagate(False)

            status_color = STATUS_COLORS.get(status, TEXT_MAIN)
            remarks_preview = (remarks[:45] + "…") if remarks and len(remarks) > 45 else (remarks or "—")

            # Clickable labels for detail view
            for widget_text, width, anchor, color, bold in [
                (name,            220, "w",      TEXT_MAIN,    False),
                (brgy,            150, "center", TEXT_MAIN,    False),
                (cat,             120, "center", TEXT_MAIN,    False),
                (status,          150, "center", status_color, True),
                (date,            100, "center", TEXT_SUB,     False),
                (remarks_preview, 260, "w",      TEXT_SUB,     False),
            ]:
                lbl = ctk.CTkLabel(row_f, text=widget_text, width=width, anchor=anchor,
                                   font=ctk.CTkFont(size=12, weight="bold" if bold else "normal"),
                                   text_color=color, cursor="hand2")
                lbl.pack(side="left", padx=(10, 0) if anchor == "w" else 0)
                lbl.bind("<Button-1>", lambda _e, r=rid: self._open_detail(r))

            # Action buttons
            act = ctk.CTkFrame(row_f, fg_color="transparent", width=110)
            act.pack(side="left")
            ctk.CTkButton(act, text="Edit", width=44, height=24,
                          fg_color=ACCENT, hover_color=ACCENT_DARK,
                          font=ctk.CTkFont(size=11),
                          command=lambda r=rid: self._open_edit(r)).pack(side="left", padx=(4, 2))
            ctk.CTkButton(act, text="Del", width=38, height=24,
                          fg_color=DANGER, hover_color="#a93226",
                          font=ctk.CTkFont(size=11),
                          command=lambda r=rid, n=name: self._delete(r, n)).pack(side="left", padx=2)

    def _open_detail(self, record_id):
        with db_connect() as con:
            row = con.execute(
                "SELECT name, barangay, category, status, date, remarks FROM solicitations WHERE id = ?",
                (record_id,)
            ).fetchone()

        if not row:
            return

        name, brgy, cat, status, date, remarks = row

        win = ctk.CTkToplevel(self)
        win.title("Record Detail")
        win.geometry("500x400")
        win.grab_set()
        win.configure(fg_color=SURFACE)

        # Header strip
        hdr = ctk.CTkFrame(win, fg_color=ACCENT, corner_radius=0, height=50)
        hdr.pack(fill="x")
        hdr.pack_propagate(False)
        ctk.CTkLabel(hdr, text=f"  {name}",
                     font=ctk.CTkFont(family="Georgia", size=15, weight="bold"),
                     text_color="white", anchor="w").pack(side="left", padx=10, fill="y")

        body = ctk.CTkFrame(win, fg_color=SURFACE)
        body.pack(fill="both", expand=True, padx=24, pady=18)

        def detail_row(label, value, val_color=TEXT_MAIN):
            r = ctk.CTkFrame(body, fg_color="transparent")
            r.pack(fill="x", pady=4)
            ctk.CTkLabel(r, text=label, width=110, anchor="w",
                         font=ctk.CTkFont(size=12, weight="bold"),
                         text_color=TEXT_SUB).pack(side="left")
            ctk.CTkLabel(r, text=value, anchor="w",
                         font=ctk.CTkFont(size=12),
                         text_color=val_color).pack(side="left")

        detail_row("Barangay:",  brgy)
        detail_row("Category:",  cat)
        detail_row("Date:",      date)
        detail_row("Status:",    status, STATUS_COLORS.get(status, TEXT_MAIN))

        divider(body)

        ctk.CTkLabel(body, text="Remarks",
                     font=ctk.CTkFont(size=12, weight="bold"),
                     text_color=TEXT_SUB).pack(anchor="w", pady=(4, 4))

        remarks_box = ctk.CTkTextbox(body, height=120,
                                     font=ctk.CTkFont(family="Courier New", size=12),
                                     border_width=1, border_color=BORDER,
                                     state="disabled")
        remarks_box.pack(fill="both", expand=True)
        remarks_box.configure(state="normal")
        remarks_box.insert("1.0", remarks or "No remarks recorded.")
        remarks_box.configure(state="disabled")

        ctk.CTkButton(body, text="Close", height=34,
                      fg_color="#6c757d", hover_color="#5a6268",
                      command=win.destroy).pack(fill="x", pady=(12, 0))

    def _open_edit(self, record_id):
        with db_connect() as con:
            row = con.execute(
                "SELECT name, barangay, category, status, remarks FROM solicitations WHERE id = ?",
                (record_id,)
            ).fetchone()

        if not row:
            return

        name, brgy, cat, status, remarks = row

        win = ctk.CTkToplevel(self)
        win.title("Edit Record")
        win.geometry("500x480")
        win.grab_set()
        win.configure(fg_color=SURFACE)

        # Header strip
        hdr = ctk.CTkFrame(win, fg_color=ACCENT, corner_radius=0, height=50)
        hdr.pack(fill="x")
        hdr.pack_propagate(False)
        ctk.CTkLabel(hdr, text=f"  Editing: {name}",
                     font=ctk.CTkFont(family="Georgia", size=14, weight="bold"),
                     text_color="white", anchor="w").pack(side="left", padx=10, fill="y")

        # ── Tab bar inside popup ──
        tab_bar = ctk.CTkFrame(win, fg_color=TAB_IDLE_BG, corner_radius=0, height=36)
        tab_bar.pack(fill="x")
        tab_bar.pack_propagate(False)

        content_area = ctk.CTkFrame(win, fg_color=SURFACE, corner_radius=0)
        content_area.pack(fill="both", expand=True)

        # ── Tab panels ──
        panel_status  = ctk.CTkFrame(content_area, fg_color=SURFACE, corner_radius=0)
        panel_remarks = ctk.CTkFrame(content_area, fg_color=SURFACE, corner_radius=0)

        for p in (panel_status, panel_remarks):
            p.place(relx=0, rely=0, relwidth=1, relheight=1)

        # Status panel contents
        sf = ctk.CTkFrame(panel_status, fg_color=SURFACE)
        sf.pack(fill="both", expand=True, padx=24, pady=18)

        section_label(sf, "Barangay").pack(anchor="w", pady=(0, 2))
        ctk.CTkLabel(sf, text=brgy, font=ctk.CTkFont(size=13),
                     text_color=TEXT_MAIN).pack(anchor="w", pady=(0, 10))

        section_label(sf, "Category").pack(anchor="w", pady=(0, 2))
        ctk.CTkLabel(sf, text=cat, font=ctk.CTkFont(size=13),
                     text_color=TEXT_MAIN).pack(anchor="w", pady=(0, 10))

        section_label(sf, "Status").pack(anchor="w", pady=(0, 2))
        status_var = ctk.StringVar(value=status)
        ctk.CTkOptionMenu(sf, variable=status_var, values=STATUSES,
                          height=34).pack(fill="x", pady=(0, 10))

        # Remarks panel contents
        rf = ctk.CTkFrame(panel_remarks, fg_color=SURFACE)
        rf.pack(fill="both", expand=True, padx=24, pady=18)

        section_label(rf, "Additional Remarks").pack(anchor="w", pady=(0, 6))
        remarks_box = ctk.CTkTextbox(rf, height=220,
                                     font=ctk.CTkFont(family="Courier New", size=12),
                                     border_width=1, border_color=BORDER)
        remarks_box.pack(fill="both", expand=True)
        if remarks:
            remarks_box.insert("1.0", remarks)

        # ── Tab switching ──
        tab_btns = {}

        def switch_edit_tab(name):
            if name == "Status":
                panel_status.tkraise()
            else:
                panel_remarks.tkraise()
            for n, b in tab_btns.items():
                if n == name:
                    b.configure(fg_color=ACCENT, text_color="white",
                                hover_color=ACCENT_DARK)
                else:
                    b.configure(fg_color=TAB_IDLE_BG, text_color=TAB_IDLE_TEXT,
                                hover_color=TAB_IDLE_BG)

        for tab_name in ("Status", "Remarks"):
            b = ctk.CTkButton(tab_bar, text=tab_name, width=120, height=36,
                              fg_color=TAB_IDLE_BG, hover_color=TAB_IDLE_BG,
                              text_color=TAB_IDLE_TEXT,
                              font=ctk.CTkFont(size=12, weight="bold"),
                              corner_radius=0,
                              command=lambda n=tab_name: switch_edit_tab(n))
            b.pack(side="left")
            tab_btns[tab_name] = b

        switch_edit_tab("Status")

        # ── Save button ──
        def _save_edit():
            new_status  = status_var.get()
            new_remarks = remarks_box.get("1.0", "end-1c").strip()
            with db_connect() as con:
                con.execute(
                    "UPDATE solicitations SET status = ?, remarks = ? WHERE id = ?",
                    (new_status, new_remarks, record_id)
                )
                con.commit()
            win.destroy()
            self._load()

        btn_row = ctk.CTkFrame(win, fg_color=SURFACE)
        btn_row.pack(fill="x", padx=24, pady=(0, 16))
        ctk.CTkButton(btn_row, text="Save Changes", height=36,
                      fg_color=ACCENT, hover_color=ACCENT_DARK,
                      font=ctk.CTkFont(size=13, weight="bold"),
                      command=_save_edit).pack(fill="x")

    def _delete(self, record_id, name):
        if messagebox.askyesno("Confirm Delete",
                               f"Delete record for {name}?\nThis cannot be undone."):
            with db_connect() as con:
                con.execute("DELETE FROM solicitations WHERE id = ?", (record_id,))
                con.commit()
            self._load()


# ── Main App Window ───────────────────────────────────────────────────────────
class SolicitationTrackerApp(ctk.CTk):
    TABS = [
        ("📋  Log Request", LogTab),
        ("📄  Records",     ListTab),
    ]

    def __init__(self):
        super().__init__()
        self.title("Solicitation Tracker")
        self.geometry("1060x680")
        self.minsize(900, 560)
        self.configure(fg_color=SURFACE)

        init_db()

        self._active_tab   = None
        self._tab_buttons  = {}
        self._tab_panels   = {}

        self._build_ui()
        self._switch_tab("📋  Log Request")

    def _build_ui(self):
        # ── Header bar ──
        hdr = ctk.CTkFrame(self, fg_color=ACCENT, corner_radius=0, height=58)
        hdr.pack(fill="x")
        hdr.pack_propagate(False)

        ctk.CTkLabel(hdr,
                     text="  🏛  Solicitation Tracker",
                     font=ctk.CTkFont(family="Georgia", size=20, weight="bold"),
                     text_color="#FFFFFF", anchor="w").pack(side="left", padx=20)

        self._clock = ctk.CTkLabel(hdr, text="",
                                   font=ctk.CTkFont(size=12),
                                   text_color="#A9CCE3")
        self._clock.pack(side="right", padx=20)
        self._tick()

        # ── Tab bar ──
        tab_bar = ctk.CTkFrame(self, fg_color=TAB_IDLE_BG, corner_radius=0, height=42)
        tab_bar.pack(fill="x")
        tab_bar.pack_propagate(False)

        for name, _ in self.TABS:
            btn = ctk.CTkButton(
                tab_bar, text=name,
                command=lambda n=name: self._switch_tab(n),
                fg_color=TAB_IDLE_BG,
                hover_color=TAB_IDLE_BG,
                text_color=TAB_IDLE_TEXT,
                font=ctk.CTkFont(size=13, weight="bold"),
                height=42, width=170,
                corner_radius=0,
            )
            btn.pack(side="left")
            self._tab_buttons[name] = btn

        # ── Content area ──
        content = ctk.CTkFrame(self, fg_color=SURFACE, corner_radius=0)
        content.pack(fill="both", expand=True)
        content.columnconfigure(0, weight=1)
        content.rowconfigure(0, weight=1)

        for name, TabClass in self.TABS:
            panel = TabClass(content)
            panel.grid(row=0, column=0, sticky="nsew")
            self._tab_panels[name] = panel

    def _switch_tab(self, name):
        if self._active_tab == name:
            return
        self._active_tab = name

        for tab_name, btn in self._tab_buttons.items():
            if tab_name == name:
                btn.configure(fg_color=ACCENT, hover_color=ACCENT_DARK,
                              text_color="#FFFFFF")
            else:
                btn.configure(fg_color=TAB_IDLE_BG, hover_color=TAB_IDLE_BG,
                              text_color=TAB_IDLE_TEXT)

        panel = self._tab_panels[name]
        panel.tkraise()

        # Refresh records list when switching to it
        if name == "📄  Records" and hasattr(panel, "_load"):
            panel._load()

    def _tick(self):
        self._clock.configure(
            text=datetime.datetime.now().strftime("  %A, %B %d %Y   %H:%M:%S"))
        self.after(1000, self._tick)


# ── Entry point ───────────────────────────────────────────────────────────────
if __name__ == "__main__":
    app = SolicitationTrackerApp()
    app.mainloop()