# 🏛 Solicitation Tracker
**Office Management System for Solicitation Requests**

---

## Overview

The Solicitation Tracker is a desktop application designed to help office staff log, manage, and monitor incoming solicitation requests from residents. It replaces manual logbooks with a clean, searchable database — tracking each resident's request from submission through to pick-up.

Built with Python and CustomTkinter, styled in Philippine flag blue.

---

## Features

### 📋 Log Request
- Enter a resident's full name, barangay, category, and initial status
- Check off requirements submitted (Valid ID, Barangay Certificate, Medical Certificate)
- Add free-form remarks per request
- **Duplicate detection** — warns you in real time if the resident already has an existing record

### 📄 Solicitation Records
- View all logged requests in a sortable, scrollable table
- **Filter by status** (Pending, Processing, Ready for Pick-up) or search by name
- **Click any row** to open a full detail view of the record
- **Edit button** — opens a tabbed popup to edit all fields: Name, Barangay, Category, Status, and Remarks
- **Delete button** — removes a record with a confirmation prompt
- Status labels are color-coded:
  - 🔴 **Pending**
  - 🟡 **Processing**
  - 🟢 **Ready for Pick-up**

### 📤 Export CSV
- Exports whatever records are currently visible (respects active search and status filter)
- Saves as a `.csv` file with a date-stamped filename
- Opens directly in Excel or any spreadsheet app

### 📥 Import CSV
- Imports records from a `.csv` file
- Accepts headers in any order and any capitalization
- Skips duplicate entries (matched by Name + Date)
- Shows a summary after import: how many were imported, skipped, or invalid

---

## Request Categories

| Category    | Description                          |
|-------------|--------------------------------------|
| Medical     | Treatment or medication assistance   |
| Financial   | Daily basic needs support            |
| Burial      | Assistance for deceased relatives    |
| Educational | School semester assistance           |
| Others      | Custom / miscellaneous requests      |

---

## File & Data Storage

| File | Location |
|------|----------|
| `solicitation_tracker.exe` | Anywhere (Desktop recommended) |
| `solicitation_tracker.db` | `C:\Users\YourName\Documents\` |

The database is created automatically on first launch. You do not need to set anything up — just run the `.exe`.

> ⚠️ Do not delete the `.db` file in Documents unless you intend to wipe all records. Back it up regularly by copying it to another folder or drive.

---

## CSV Format

When importing, the CSV must contain these columns (case and order don't matter):

| Column     | Required | Notes                                      |
|------------|----------|--------------------------------------------|
| `Name`     | ✅ Yes   | Automatically converted to uppercase       |
| `Barangay` | ✅ Yes   |                                            |
| `Category` | ✅ Yes   |                                            |
| `Status`   | ✅ Yes   | Must be: Pending, Processing, Ready for Pick-up |
| `Date`     | ✅ Yes   | Format: YYYY-MM-DD                         |
| `Remarks`  | ❌ No    | Optional, can be blank                     |

The exported CSV from this app is already in the correct format and can be re-imported safely.

---

## Running from Source

**Requirements:**
```
python >= 3.10
customtkinter
```

**Install dependencies:**
```bash
pip install customtkinter
```

**Run:**
```bash
python solicitation_tracker.py
```

---

## Building the Executable

```bash
pip install pyinstaller
pyinstaller --onefile --windowed --name "SolicitationTracker" solicitation_tracker.py
```

The `.exe` will be in the `dist/` folder. Place it wherever you like — the database will always save to your Documents folder regardless.

---

## Notes

- The app window opens at **1060 × 680** and can be resized
- All records are stored locally — no internet connection required
- The app does not generate or print any documents; it is purely a tracker

---

*Developed for internal office use.*
