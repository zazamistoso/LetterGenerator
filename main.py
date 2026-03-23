import os
import sqlite3
import customtkinter as ctk
from docx import Document
from datetime import datetime
import sys

ctk.set_appearance_mode("light") 
ctk.set_default_color_theme("blue")

# --- SMART FIX: PORTABLE PATHS ---
def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

class MakatiApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Makati Document Generator & Tracker")
        self.geometry("1000x850")

        self.blue = "#0038A8"
        self.yellow = "#FFD700"

        # Define your Office Font style here
        self.header_font = ctk.CTkFont(family="Arial", size=24, weight="bold")
        self.body_font = ctk.CTkFont(family="Arial", size=14)
        self.sidebar_font = ctk.CTkFont(family="Helvetica", size=13, weight="bold")

        # Setup Output Folder
        self.output_folder = os.path.join(os.path.abspath("."), "Generated Letters")
        if not os.path.exists(self.output_folder):
            os.makedirs(self.output_folder)

        self.templates = {
            "Medical": "regarding medical assistance for their treatment/medication at [INSERT HOSPITAL NAME].",
            "Financial": "regarding their request for financial assistance to [INSERT REASON FOR THE FINANCIAL ASSISTANCE]",
            "Burial": "regarding their request for burial assistance for their deceased relative.",
            "Educational": "regarding their request for educational assistance for the upcoming school semester.",
            "Others": "regarding [INSERT SPECIFIC REQUEST HERE]."
        }

        self.init_db()

        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # Sidebar
        self.sidebar_frame = ctk.CTkFrame(self, width=200, corner_radius=0, fg_color=self.blue)
        self.sidebar_frame.grid(row=0, column=0, sticky="nsew")
        
        self.logo_label = ctk.CTkLabel(self.sidebar_frame, text="Main Menu", 
                                       font=ctk.CTkFont(size=20, weight="bold"), text_color="white")
        self.logo_label.grid(row=0, column=0, padx=20, pady=(20, 10))

        # Buttons with Yellow Hover Effect
        self.btn_home = ctk.CTkButton(self.sidebar_frame, 
                                      text="Home", 
                                      font=self.sidebar_font, # <--- Apply here
                                      fg_color="transparent", 
                                      hover_color=self.yellow)
        self.btn_home.grid(row=1, column=0, padx=20, pady=10)

        self.btn_draft = ctk.CTkButton(self.sidebar_frame, text="Draft Letter", 
                                       fg_color="transparent", hover_color=self.yellow,
                                       text_color="white", command=self.show_draft_view)
        self.btn_draft.grid(row=2, column=0, padx=20, pady=10)

        self.btn_list = ctk.CTkButton(self.sidebar_frame, text="Solicitation List", 
                                      fg_color="transparent", hover_color=self.yellow,
                                      text_color="white", command=self.show_list_view)
        self.btn_list.grid(row=3, column=0, padx=20, pady=10)

        self.main_view = ctk.CTkFrame(self, corner_radius=10, fg_color="transparent")
        self.main_view.grid(row=0, column=1, padx=20, pady=20, sticky="nsew")
        
        self.show_home_view()

    # --- DATABASE LOGIC ---
    def init_db(self):
        db_path = resource_path("office_tracker.db")
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS records 
                          (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                           name TEXT, barangay TEXT, type TEXT, 
                           date TEXT, filename TEXT)''')
        conn.commit()
        conn.close()

    def clear_view(self):
        for widget in self.main_view.winfo_children():
            widget.destroy()

    # --- VIEW: HOME ---
    def show_home_view(self):
        self.clear_view()
        welcome_label = ctk.CTkLabel(self.main_view, text="Welcome!", font=ctk.CTkFont(size=50, weight="bold"))
        welcome_label.pack(pady=(40, 10))
        sub_label = ctk.CTkLabel(self.main_view, text="Automated Letter Generator", font=ctk.CTkFont(size=25))
        sub_label.pack(pady=5)
        quick_start = ctk.CTkButton(self.main_view, text="Create New Letter", width=200, height=50, command=self.show_draft_view)
        quick_start.pack(pady=40)

    # --- VIEW: DRAFT ---
    def show_draft_view(self):
        self.clear_view()
        
        # 1. Main Title
        title = ctk.CTkLabel(self.main_view, text="New Letter Draft", 
                             font=ctk.CTkFont(family="Arial", size=22, weight="bold"))
        title.pack(pady=(5, 5))

        # 2. Input Form Frame
        form_frame = ctk.CTkFrame(self.main_view)
        form_frame.pack(fill="x", padx=20, pady=5)

        left_input = ctk.CTkFrame(form_frame, fg_color="transparent")
        left_input.pack(side="left", fill="both", expand=True, padx=20, pady=5)

        ctk.CTkLabel(left_input, text="Resident Full Name:").pack(anchor="w")
        self.name_entry = ctk.CTkEntry(left_input, placeholder_text="e.g. JUAN DELA CRUZ", width=300)
        self.name_entry.pack(pady=(2, 5), anchor="w")

        ctk.CTkLabel(left_input, text="Barangay & Request:").pack(anchor="w")
        
        combo_frame = ctk.CTkFrame(left_input, fg_color="transparent")
        combo_frame.pack(fill="x", anchor="w")
        
        self.brgy_opt = ctk.CTkComboBox(combo_frame, values=["Viejo", "Nuevo", "Pinagkaisahan"], width=145)
        self.brgy_opt.pack(side="left", padx=(0, 10))
        
        self.req_opt = ctk.CTkComboBox(combo_frame, values=list(self.templates.keys()), width=145)
        self.req_opt.pack(side="left")

        # Use self.blue and self.yellow
        self.btn_auto = ctk.CTkButton(left_input, text="Auto-Fill Draft", height=28, 
                                      fg_color=self.blue, hover_color=self.yellow,
                                      command=self.update_draft)
        self.btn_auto.pack(pady=10, anchor="w")

        # 3. Requirements (Right side)
        right_check = ctk.CTkFrame(form_frame, width=220)
        right_check.pack(side="right", fill="y", padx=20, pady=5)
        ctk.CTkLabel(right_check, text="Requirements", font=ctk.CTkFont(weight="bold")).pack(pady=2)
        
        self.id_check = ctk.CTkCheckBox(right_check, text="ID", checkbox_width=18, checkbox_height=18)
        self.id_check.pack(anchor="w", padx=10, pady=1)
        self.ind_check = ctk.CTkCheckBox(right_check, text="Brgy. Certificate", checkbox_width=18, checkbox_height=18)
        self.ind_check.pack(anchor="w", padx=10, pady=1)
        self.med_check = ctk.CTkCheckBox(right_check, text="Med. Certificate", checkbox_width=18, checkbox_height=18)
        self.med_check.pack(anchor="w", padx=10, pady=1)

        # 4. Header Box (Times New Roman for official feel)
        ctk.CTkLabel(self.main_view, text="Edit Header:").pack(anchor="w", padx=40)
        self.letter_header = ctk.CTkTextbox(self.main_view, height=90, font=("Times New Roman", 13)) 
        self.letter_header.pack(fill="x", padx=40, pady=2)
        
        current_date = datetime.now().strftime("%B %d, %Y")
        header_content = f"{current_date}\n\n\n\n"
        header_content += "OFFICE OF THE COUNCILOR\nDistrict 2, Makati City Hall"
        self.letter_header.insert("1.0", header_content)

        # 5. Body Box (Times New Roman for official feel)
        ctk.CTkLabel(self.main_view, text="Edit Body Content:").pack(anchor="w", padx=40)
        self.letter_body = ctk.CTkTextbox(self.main_view, height=140, font=("Times New Roman", 13))
        self.letter_body.pack(fill="x", padx=40, pady=2)

        # 6. Generate Button (Makati Themed)
        self.save_btn = ctk.CTkButton(self.main_view, text="Generate Word Document", 
                                      fg_color=self.blue, hover_color=self.yellow, 
                                      height=40, command=self.generate_and_open)
        self.save_btn.pack(pady=15)

    def update_draft(self):
        name = self.name_entry.get().upper()
        req_type = self.req_opt.get()
        template_text = self.templates.get(req_type, "")

        if not name:
            # Optional: Add a popup here later to tell user to enter a name
            return

        # 1. Start with the main template
        full_body = f"This is to formally endorse the request of {name}, a resident of Barangay {self.brgy_opt.get()}, {template_text}\n\n"

        # 2. Check which requirements are ticked
        attachments = []
        if self.id_check.get(): attachments.append("Government Issued ID")
        if self.ind_check.get(): attachments.append("Barangay Certificate")
        if self.med_check.get(): attachments.append("Medical Certificate")

        # 3. Add the "Attachments" sentence if any boxes are checked
        if attachments:
            # Join them with commas, e.g., "ID, Barangay Certificate, and Medical Certificate"
            attachment_list = ", ".join(attachments[:-1]) + (f" and {attachments[-1]}" if len(attachments) > 1 else attachments[0])
            full_body += f"For your reference, I have attached their {attachment_list} to support this request."

        # 4. Update the Textbox
        self.letter_body.delete("1.0", "end")
        self.letter_body.insert("1.0", full_body)

    # --- VIEW: SOLICITATION LIST ---
    def show_list_view(self):
        self.clear_view()
        title = ctk.CTkLabel(self.main_view, text="Solicitation Tracker", font=ctk.CTkFont(size=24, weight="bold"))
        title.pack(pady=10)

        # 1. Search Bar (Dropdown is removed for a cleaner look)
        filter_frame = ctk.CTkFrame(self.main_view, fg_color="transparent")
        filter_frame.pack(fill="x", padx=20, pady=5)
        
        self.search_entry = ctk.CTkEntry(filter_frame, placeholder_text="Search resident name...", width=400)
        self.search_entry.pack(side="left", padx=10)
        self.search_entry.bind("<KeyRelease>", lambda event: self.load_records())

        # 2. Clickable Table Headers
        header_frame = ctk.CTkFrame(self.main_view, fg_color="gray30", corner_radius=0)
        header_frame.pack(fill="x", padx=20, pady=(10,0))
        
        # We check if a sort is already set; if not, default to newest entries
        if not hasattr(self, 'current_sort'):
            self.current_sort = "id DESC"

        # Helper function to update sort and refresh list
        def set_sort(column_sql):
            self.current_sort = column_sql
            self.load_records()

        # Resident Name Header
        ctk.CTkButton(header_frame, text="Resident Name", fg_color="transparent", hover_color="gray40",
                      anchor="w", width=250, text_color="white",
                      command=lambda: set_sort("name ASC")).grid(row=0, column=0, padx=(20, 0))
        
        # Barangay Header
        ctk.CTkButton(header_frame, text="Barangay", fg_color="transparent", hover_color="gray40",
                      width=120, text_color="white",
                      command=lambda: set_sort("barangay ASC")).grid(row=0, column=1)
        
        # Type Header
        ctk.CTkButton(header_frame, text="Type", fg_color="transparent", hover_color="gray40",
                      width=120, text_color="white",
                      command=lambda: set_sort("type ASC")).grid(row=0, column=2)
        
        # Date Header
        ctk.CTkButton(header_frame, text="Date Generated", fg_color="transparent", hover_color="gray40",
                      width=180, text_color="white",
                      command=lambda: set_sort("date DESC")).grid(row=0, column=3)

        ctk.CTkLabel(header_frame, text="Action", width=100, text_color="white").grid(row=0, column=4)

        # 3. List Container
        self.scroll_frame = ctk.CTkScrollableFrame(self.main_view, height=500, corner_radius=0)
        self.scroll_frame.pack(fill="both", expand=True, padx=20, pady=(0, 10))

        self.load_records()

    def load_records(self):
        # Clear the UI
        for widget in self.scroll_frame.winfo_children():
            widget.destroy()

        # Get search text and current sort column
        search_query = self.search_entry.get().upper()
        order_by = getattr(self, 'current_sort', 'id DESC')

        db_path = resource_path("office_tracker.db")
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Combined query: Filters by name and Sorts by the clicked header
        query = f"SELECT name, barangay, type, date, filename, id FROM records WHERE name LIKE ? ORDER BY {order_by}"
        cursor.execute(query, (f'%{search_query}%',))
        rows = cursor.fetchall()
        
        for row in rows:
            name, brgy, req_type, date, filename, db_id = row
            if not os.path.exists(filename): continue 
            
            row_frame = ctk.CTkFrame(self.scroll_frame, fg_color="transparent")
            row_frame.pack(fill="x")
            
            ctk.CTkLabel(row_frame, text=name, width=250, anchor="w").grid(row=0, column=0, padx=(20, 0), pady=5)
            ctk.CTkLabel(row_frame, text=brgy, width=120).grid(row=0, column=1)
            ctk.CTkLabel(row_frame, text=req_type, width=120).grid(row=0, column=2)
            ctk.CTkLabel(row_frame, text=date, width=180).grid(row=0, column=3)
            
            btn_view = ctk.CTkButton(row_frame, text="Open", width=80, height=24,
                                     command=lambda f=filename: os.startfile(f))
            btn_view.grid(row=0, column=4, padx=(10, 0))
        
        conn.close()

    def generate_and_open(self):
        header_text = self.letter_header.get("1.0", "end-1c")
        body_text = self.letter_body.get("1.0", "end-1c")
        raw_name = self.name_entry.get().upper() if self.name_entry.get() else "DRAFT"
        clean_name = raw_name.replace(" ", "_")

        file_name = f"Endorsement_{clean_name}.docx"
        full_path = os.path.join(self.output_folder, file_name)

        doc = Document()
        doc.add_paragraph(header_text)
        doc.add_paragraph("\n\n")
        doc.add_paragraph(body_text)
        doc.save(full_path)

        db_path = resource_path("office_tracker.db")
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
        cursor.execute("INSERT INTO records (name, barangay, type, date, filename) VALUES (?, ?, ?, ?, ?)",
                       (raw_name, self.brgy_opt.get(), self.req_opt.get(), timestamp, full_path))
        conn.commit()
        conn.close()

        try:
            os.startfile(full_path)
        except Exception as e:
            print(f"Error opening file: {e}")

if __name__ == "__main__":
    app = MakatiApp()
    app.mainloop()