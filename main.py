import os
import sqlite3
import customtkinter as ctk
from docx import Document
import datetime  # FIXED: Needed for the auto-updating date
import sys
import win32api

ctk.set_appearance_mode("light") 
ctk.set_default_color_theme("blue")

def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

class LetterGeneratorApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Automated Document Generator & Tracker")
        self.geometry("1000x850")

        self.blue = "#0038A8"
        self.yellow = "#FFD700"

        self.sidebar_font = ctk.CTkFont(family="Helvetica", size=13, weight="bold")

        # Setup Output Folder
        self.output_folder = os.path.join(os.path.abspath("."), "Generated Letters")
        if not os.path.exists(self.output_folder):
            os.makedirs(self.output_folder)

        self.init_db()

        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # Sidebar
        self.sidebar_frame = ctk.CTkFrame(self, width=200, corner_radius=0, fg_color=self.blue)
        self.sidebar_frame.grid(row=0, column=0, sticky="nsew")
        
        ctk.CTkLabel(self.sidebar_frame, text="Main Menu", font=ctk.CTkFont(size=20, weight="bold"), text_color="white").grid(row=0, column=0, padx=20, pady=(20, 10))

        # Sidebar Navigation
        ctk.CTkButton(self.sidebar_frame, text="Home", fg_color="transparent", hover_color=self.yellow, command=self.show_home_view).grid(row=1, column=0, padx=20, pady=10)
        ctk.CTkButton(self.sidebar_frame, text="Draft Letter", fg_color="transparent", hover_color=self.yellow, command=self.show_draft_view).grid(row=2, column=0, padx=20, pady=10)
        ctk.CTkButton(self.sidebar_frame, text="Solicitation List", fg_color="transparent", hover_color=self.yellow, command=self.show_list_view).grid(row=3, column=0, padx=20, pady=10)
        ctk.CTkButton(self.sidebar_frame, text="Edit Templates", fg_color="transparent", hover_color=self.yellow, command=self.show_template_settings).grid(row=4, column=0, padx=20, pady=10)

        self.main_view = ctk.CTkFrame(self, corner_radius=10, fg_color="transparent")
        self.main_view.grid(row=0, column=1, padx=20, pady=20, sticky="nsew")
        
        self.show_home_view()

    def init_db(self):
        conn = sqlite3.connect(resource_path("office_tracker.db"))
        cursor = conn.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS records (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, barangay TEXT, type TEXT, date TEXT, filename TEXT)''')
        cursor.execute('''CREATE TABLE IF NOT EXISTS templates (category TEXT PRIMARY KEY, body_text TEXT)''')
        
        cursor.execute("SELECT COUNT(*) FROM templates")
        if cursor.fetchone()[0] == 0:
            default_data = [
                ("Medical", "regarding medical assistance for their treatment/medication at [INSERT HOSPITAL NAME]."),
                ("Financial", "regarding their request for financial assistance to support their daily basic needs."),
                ("Burial", "regarding their request for burial assistance for their deceased relative."),
                ("Educational", "regarding their request for educational assistance for the upcoming school semester."),
                ("Others", "regarding [INSERT SPECIFIC REQUEST HERE].")
            ]
            cursor.executemany("INSERT INTO templates (category, body_text) VALUES (?, ?)", default_data)
        conn.commit()
        conn.close()

    def clear_view(self):
        for widget in self.main_view.winfo_children():
            widget.destroy()

    def show_home_view(self):
        self.clear_view()
        ctk.CTkLabel(self.main_view, text="Welcome!", font=ctk.CTkFont(size=50, weight="bold")).pack(pady=(40, 10))
        ctk.CTkLabel(self.main_view, text="This is a letter generator app", font=ctk.CTkFont(size=25)).pack(pady=(10, 10))
        ctk.CTkButton(self.main_view, text="Create New Letter", width=200, height=50, command=self.show_draft_view).pack(pady=40)

    # --- UPDATED DRAFT VIEW ---
    def show_draft_view(self):
        self.clear_view()
        draft_container = ctk.CTkFrame(self.main_view, fg_color="transparent")
        draft_container.pack(fill="both", expand=True, padx=40, pady=15)

        # 1. Header Editor (Integrated with Date at the Top)
        ctk.CTkLabel(draft_container, text="OFFICE HEADER / LETTERHEAD", 
                     font=("Arial", 12, "bold"), text_color=self.blue).pack(anchor="w")
        
        self.header_editor = ctk.CTkTextbox(draft_container, height=80, font=("Arial", 12))
        self.header_editor.pack(fill="x", pady=(5, 15))
        
        # Format the date and set as the first line of the header
        import datetime
        today_str = datetime.date.today().strftime("%B %d, %Y")
        default_header = f"{today_str}\nCITY GOVERNMENT OF MAKATI\nMAKATI CITY HALL, DISTRICT 2\n"
        
        self.header_editor.insert("1.0", default_header)

        # 2. Inputs
        ctk.CTkLabel(draft_container, text="Resident Full Name:", font=self.sidebar_font).pack(anchor="w")
        self.name_entry = ctk.CTkEntry(draft_container, placeholder_text="Enter Name...", height=35)
        self.name_entry.pack(fill="x", pady=(2, 10))

        row_frame = ctk.CTkFrame(draft_container, fg_color="transparent")
        row_frame.pack(fill="x")
        
        self.brgy_opt = ctk.CTkOptionMenu(row_frame, values=["Guadalupe Nuevo", "Guadalupe Viejo", "Pinagkaisahan"])
        self.brgy_opt.pack(side="left", padx=(0, 10))
        
        self.req_opt = ctk.CTkOptionMenu(row_frame, values=["Medical", "Financial", "Burial", "Educational", "Others"])
        self.req_opt.pack(side="left")

        # 3. Checkboxes (Updated to Barangay Certificate)
        ctk.CTkLabel(draft_container, text="Requirements Attached:", font=self.sidebar_font).pack(anchor="w", pady=(10, 0))
        check_frame = ctk.CTkFrame(draft_container, fg_color="transparent")
        check_frame.pack(fill="x", pady=5)
        
        self.id_check = ctk.CTkCheckBox(check_frame, text="Valid ID")
        self.id_check.pack(side="left", padx=5)
        
        self.ind_check = ctk.CTkCheckBox(check_frame, text="Barangay Certificate")
        self.ind_check.pack(side="left", padx=5)
        
        self.med_check = ctk.CTkCheckBox(check_frame, text="Med. Cert")
        self.med_check.pack(side="left", padx=5)

        # 4. Preview Section
        preview_label_row = ctk.CTkFrame(draft_container, fg_color="transparent")
        preview_label_row.pack(fill="x", pady=(10, 0))
        ctk.CTkLabel(preview_label_row, text="Final Letter Preview:", font=self.sidebar_font).pack(side="left")
        
        # Refresh Button Connection
        self.btn_refresh = ctk.CTkButton(preview_label_row, text="Refresh Preview", 
                                         width=140, height=28, fg_color="#6c757d",
                                         command=self.trigger_preview_logic)
        self.btn_refresh.pack(side="right")

        self.preview_box = ctk.CTkTextbox(draft_container, height=150, font=("Times New Roman", 14), border_width=1)
        self.preview_box.pack(fill="both", expand=True, pady=10)

        # 5. Action Buttons
        btn_frame = ctk.CTkFrame(draft_container, fg_color="transparent")
        btn_frame.pack(pady=10)
        
        ctk.CTkButton(btn_frame, text="Generate Word", fg_color=self.blue, 
                      command=self.update_draft).grid(row=0, column=0, padx=10)
        
        ctk.CTkButton(btn_frame, text="Print Document", fg_color="#28a745", 
                      command=self.generate_and_print).grid(row=0, column=1, padx=10)
        
    # --- THE FIXED SUPER LOGIC ---
    def trigger_preview_logic(self):
        self.update_draft(save_only=False, preview_only=True)

    def update_draft(self, save_only=False, preview_only=False):
        # 1. Capture Header & UI Inputs
        header_text = self.header_editor.get("1.0", "end-1c")
        name = self.name_entry.get().upper()
        brgy = self.brgy_opt.get()
        req_type = self.req_opt.get()

        if not name:
            self.preview_box.delete("1.0", "end")
            self.preview_box.insert("1.0", "⚠️ Please enter a Resident Name.")
            return None

        # 2. SYNC STEP: Fetch the latest template from the Database
        conn = sqlite3.connect(resource_path("office_tracker.db"))
        cursor = conn.cursor()
        cursor.execute("SELECT body_text FROM templates WHERE category = ?", (req_type,))
        result = cursor.fetchone()
        conn.close()

        # Use the DB text if it exists; otherwise, use a fallback
        custom_body = result[0] if result else f"regarding their {req_type} assistance request."

        # 3. Checkbox Logic
        reqs = []
        if self.id_check.get(): reqs.append("Valid ID")
        if self.ind_check.get(): reqs.append("Barangay Certificate")
        if self.med_check.get(): reqs.append("Medical Certificate")
        
        attachment_str = f"\n\n\nHere are the attached requirements provided by the resident: {', '.join(reqs)}." if reqs else ""

        # 4. Final Assembly (Using the custom_body from DB)
        full_letter = (
            f"{header_text}\n\n"
            f"TO WHOM IT MAY CONCERN:\n\n"
            f"This is to formally endorse {name}, a resident of Barangay {brgy}, "
            f"{custom_body}{attachment_str}\n\n\n"
            f"Respectfully,\n\n"
            f"OFFICE OF THE COUNCILOR"
        )

        # 5. Push to Preview Box
        self.preview_box.delete("1.0", "end")
        self.preview_box.insert("1.0", full_letter)

        if preview_only:
            return None

        # 6. Save to Word
        doc = Document()
        for line in full_letter.split('\n'):
            doc.add_paragraph(line)
        
        file_name = f"Endorsement_{name.replace(' ', '_')}.docx"
        full_path = os.path.join(self.output_folder, file_name)
        doc.save(full_path)

        # 7. Log to Records
        today_db = datetime.date.today().strftime("%Y-%m-%d")
        conn = sqlite3.connect(resource_path("office_tracker.db"))
        cursor = conn.cursor()
        cursor.execute("INSERT INTO records (name, barangay, type, date, filename) VALUES (?, ?, ?, ?, ?)",
                       (name, brgy, req_type, today_db, full_path))
        conn.commit()
        conn.close()

        if not save_only:
            os.startfile(full_path)
            
        return full_path
    
    def generate_and_print(self):
        doc_path = self.update_draft(save_only=True)
        if doc_path:
            win32api.ShellExecute(0, "print", doc_path, None, ".", 0)

    # --- TEMPLATE EDITOR ---
    def show_template_settings(self):
        self.clear_view()
        ctk.CTkLabel(self.main_view, text="Template Editor", font=("Arial", 22, "bold")).pack(pady=10)
        self.edit_cat_opt = ctk.CTkComboBox(self.main_view, values=["Medical", "Financial", "Burial", "Educational", "Others"], command=self.load_template_to_editor)
        self.edit_cat_opt.pack(pady=10)
        self.template_edit_box = ctk.CTkTextbox(self.main_view, height=200)
        self.template_edit_box.pack(fill="both", expand=True, padx=40, pady=10)
        ctk.CTkButton(self.main_view, text="Update Template", command=self.save_template_changes).pack(pady=20)
        self.load_template_to_editor()

    def load_template_to_editor(self, choice=None):
        cat = self.edit_cat_opt.get()
        conn = sqlite3.connect(resource_path("office_tracker.db"))
        cursor = conn.cursor()
        cursor.execute("SELECT body_text FROM templates WHERE category = ?", (cat,))
        result = cursor.fetchone()
        self.template_edit_box.delete("1.0", "end")
        if result: self.template_edit_box.insert("1.0", result[0])
        conn.close()

    def save_template_changes(self):
        cat = self.edit_cat_opt.get()
        new_text = self.template_edit_box.get("1.0", "end-1c")
        conn = sqlite3.connect(resource_path("office_tracker.db"))
        cursor = conn.cursor()
        cursor.execute("UPDATE templates SET body_text = ? WHERE category = ?", (new_text, cat))
        conn.commit()
        conn.close()

    # --- SOLICITATION LIST ---
    # --- VIEW: SOLICITATION LIST (With restored Sorter) ---
    def show_list_view(self):
        self.clear_view()
        ctk.CTkLabel(self.main_view, text="Solicitation Tracker", font=("Arial", 24, "bold")).pack(pady=10)

        # 1. Search Bar
        filter_frame = ctk.CTkFrame(self.main_view, fg_color="transparent")
        filter_frame.pack(fill="x", padx=20, pady=5)
        self.search_entry = ctk.CTkEntry(filter_frame, placeholder_text="Search resident name...", width=400)
        self.search_entry.pack(side="left", padx=10)
        self.search_entry.bind("<KeyRelease>", lambda event: self.load_records())

        # 2. Table Headers (Updated with TYPE)
        header_frame = ctk.CTkFrame(self.main_view, fg_color="gray30", corner_radius=0)
        header_frame.pack(fill="x", padx=20, pady=(10,0))
        
        if not hasattr(self, 'current_sort'):
            self.current_sort = "id DESC"

        def set_sort(column_sql):
            self.current_sort = column_sql
            self.load_records()

        # Resident Name Header
        ctk.CTkButton(header_frame, text="Resident Name", fg_color="transparent", hover_color="gray40",
                      anchor="w", width=220, text_color="white",
                      command=lambda: set_sort("name ASC")).grid(row=0, column=0, padx=(20, 0))
        
        # Barangay Header
        ctk.CTkButton(header_frame, text="Barangay", fg_color="transparent", hover_color="gray40",
                      width=120, text_color="white",
                      command=lambda: set_sort("barangay ASC")).grid(row=0, column=1)

        # NEW: Type Header
        ctk.CTkButton(header_frame, text="Type", fg_color="transparent", hover_color="gray40",
                      width=100, text_color="white",
                      command=lambda: set_sort("type ASC")).grid(row=0, column=2)
        
        # Date Header
        ctk.CTkButton(header_frame, text="Date", fg_color="transparent", hover_color="gray40",
                      width=150, text_color="white",
                      command=lambda: set_sort("id DESC")).grid(row=0, column=3)

        ctk.CTkLabel(header_frame, text="Action", width=100, text_color="white").grid(row=0, column=4)

        # 3. List Container
        self.scroll_frame = ctk.CTkScrollableFrame(self.main_view, height=500, corner_radius=0)
        self.scroll_frame.pack(fill="both", expand=True, padx=20, pady=(0, 10))

        self.load_records()

    def load_records(self):
        for widget in self.scroll_frame.winfo_children():
            widget.destroy()

        search = self.search_entry.get().upper()
        order_by = getattr(self, 'current_sort', 'id DESC')

        conn = sqlite3.connect(resource_path("office_tracker.db"))
        cursor = conn.cursor()
        
        # Updated Query to include 'type'
        cursor.execute(f"SELECT name, barangay, type, date, filename FROM records WHERE name LIKE ? ORDER BY {order_by}", 
                       (f'%{search}%',))
        
        rows = cursor.fetchall()
        for row in rows:
            name, brgy, req_type, date, filename = row
            
            row_f = ctk.CTkFrame(self.scroll_frame, fg_color="transparent")
            row_f.pack(fill="x", pady=2)
            
            # Displaying the data in columns
            ctk.CTkLabel(row_f, text=name, width=220, anchor="w").grid(row=0, column=0, padx=(20, 0))
            ctk.CTkLabel(row_f, text=brgy, width=120).grid(row=0, column=1)
            ctk.CTkLabel(row_f, text=req_type, width=100).grid(row=0, column=2)
            ctk.CTkLabel(row_f, text=date, width=150).grid(row=0, column=3)
            
            ctk.CTkButton(row_f, text="Open", width=80, height=24,
                          command=lambda path=filename: self.safe_open(path)).grid(row=0, column=4, padx=10)
        
        conn.close()

    def safe_open(self, path):
        if os.path.exists(path):
            os.startfile(path)
        else:
            print("File no longer exists.")

if __name__ == "__main__":
    app = LetterGeneratorApp()
    app.mainloop()