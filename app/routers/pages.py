from nicegui import ui
from fastapi import FastAPI
import requests
import pandas as pd

API_BASE = "http://localhost:8000"

def create_dashboard():
    ui.page_title("GradePulse Dashboard")

    def refresh_table():
        resp = requests.get(f"{API_BASE}/grades/")
        if resp.status_code == 200:
            rows = resp.json()
            table.rows = rows
            update_stats()
        else:
            ui.notify("Failed to load grades", type="negative")

    def update_stats():
        resp = requests.get(f"{API_BASE}/grades/stats/summary")
        if resp.status_code == 200:
            stats = resp.json()
            stats_card_1.set_text(f"Total Students: {stats['total_students']}")
            stats_card_2.set_text(f"Avg %: {stats['avg_percentage']}%")
            stats_card_3.set_text(f"Total Records: {stats['total_records']}")
            stats_card_4.set_text(f"Highest: {stats['highest_scorer']}")

    def delete_grade(grade_id):
        def confirm():
            resp = requests.delete(f"{API_BASE}/grades/{grade_id}")
            if resp.status_code == 200:
                ui.notify("Deleted", type="positive")
                refresh_table()
            else:
                ui.notify("Delete failed", type="negative")
        with ui.dialog() as dialog, ui.card():
            ui.label("Are you sure you want to delete this grade?")
            with ui.row():
                ui.button("Yes", on_click=lambda: [confirm(), dialog.close()])
                ui.button("No", on_click=dialog.close)
        dialog.open()

    def get_tips(grade_id):
        resp = requests.post(f"{API_BASE}/grades/{grade_id}/study-tips")
        if resp.status_code == 200:
            tips = resp.json()["study_tips"]
            with ui.dialog() as dialog, ui.card():
                ui.label(tips)
                ui.button("Close", on_click=dialog.close)
            dialog.open()
        else:
            ui.notify("AI tips failed", type="negative")

    def show_add_dialog():
        with ui.dialog() as dialog, ui.card():
            student = ui.input("Student Name")
            father = ui.input("Father Name (optional)")
            subject = ui.input("Subject")
            marks_obtained = ui.number("Marks Obtained", value=0, step=1)
            total_marks = ui.number("Total Marks", value=100, step=1)
            exam_type = ui.select("Exam Type", ["Combined", "Theory", "Practical"], value="Combined")
            semester = ui.input("Semester", value="Spring 2025")
            date = ui.input("Date (YYYY-MM-DD)", value="2025-01-01")
            percent_label = ui.label("Percentage: 0%")

            def update_percent():
                m = marks_obtained.value or 0
                t = total_marks.value or 1
                p = (m / t) * 100
                percent_label.set_text(f"Percentage: {p:.1f}%")

            marks_obtained.on("change", update_percent)
            total_marks.on("change", update_percent)

            def submit():
                payload = {
                    "student_name": student.value,
                    "father_name": father.value or None,
                    "subject": subject.value,
                    "marks_obtained": marks_obtained.value,
                    "total_marks": total_marks.value,
                    "exam_type": exam_type.value,
                    "semester": semester.value,
                    "date": date.value,
                }
                resp = requests.post(f"{API_BASE}/grades/", json=payload)
                if resp.status_code == 200:
                    dialog.close()
                    refresh_table()
                    ui.notify("Grade added", type="positive")
                else:
                    ui.notify("Error: " + resp.text, type="negative")
            ui.button("Save", on_click=submit)
        dialog.open()

    with ui.header(elevated=True).classes("items-center justify-between"):
        ui.image("logo.png").classes("w-12 h-12")
        ui.label("GradePulse").classes("text-2xl font-bold")
        ui.space()
        ui.button(icon="dark_mode", on_click=lambda: ui.dark_mode().toggle()).props("flat")

    with ui.left_drawer().classes("bg-blue-100"):
        ui.link("Dashboard", "/").classes("text-black")
        ui.link("Analytics", "/analytics").classes("text-black")
        ui.link("Upload File", "/upload").classes("text-black")
        ui.link("About", "/about").classes("text-black")

    with ui.row().classes("w-full p-4 gap-4"):
        stats_card_1 = ui.card().classes("flex-1")
        stats_card_2 = ui.card().classes("flex-1")
        stats_card_3 = ui.card().classes("flex-1")
        stats_card_4 = ui.card().classes("flex-1")

    with ui.card():
        search = ui.input("Search by student name").on("change", lambda e: table.filter(e.value))
        columns = [
            {"name": "id", "label": "ID", "field": "id", "align": "left"},
            {"name": "student_name", "label": "Student", "field": "student_name"},
            {"name": "subject", "label": "Subject", "field": "subject"},
            {"name": "marks_obtained", "label": "Obtained", "field": "marks_obtained"},
            {"name": "total_marks", "label": "Total", "field": "total_marks"},
            {"name": "exam_type", "label": "Type", "field": "exam_type"},
            {"name": "semester", "label": "Semester", "field": "semester"},
            {"name": "date", "label": "Date", "field": "date"},
        ]
        table = ui.table(columns=columns, rows=[], row_key="id").classes("w-full")
        table.add_slot("body-cell-actions", """
            <q-td key="actions" :props="props">
                <q-btn flat round icon="edit" @click="edit(props.row.id)"></q-btn>
                <q-btn flat round icon="delete" @click="deleteRow(props.row.id)"></q-btn>
                <q-btn flat round icon="lightbulb" @click="tips(props.row.id)"></q-btn>
            </q-td>
        """)
        refresh_table()

    ui.button("➕ Add Grade", on_click=show_add_dialog, icon="add").classes("fixed bottom-4 right-4 z-50")

def create_analytics():
    ui.page_title("Analytics")
    with ui.header():
        ui.link("Back to Dashboard", "/")
    with ui.left_drawer():
        ui.link("Dashboard", "/")
        ui.link("Analytics", "/analytics")
        ui.link("Upload File", "/upload")
        ui.link("About", "/about")
    resp = requests.get(f"{API_BASE}/grades/")
    if resp.status_code == 200:
        data = resp.json()
        if data:
            df = pd.DataFrame(data)
            subject_avg = df.groupby("subject").apply(lambda x: (x["marks_obtained"] / x["total_marks"] * 100).mean()).reset_index()
            subject_avg.columns = ["subject", "avg_percentage"]
            ui.label("Subject-wise Average Percentage").classes("text-xl p-4")
            ui.table(columns=[{"name": "subject", "label": "Subject"}, {"name": "avg_percentage", "label": "Avg %"}], rows=subject_avg.to_dict("records"))
        else:
            ui.label("No data for analytics")
    else:
        ui.label("Failed to load grades")

def create_upload_page():
    ui.page_title("Upload File")
    with ui.header():
        ui.link("Dashboard", "/")
    with ui.left_drawer():
        ui.link("Dashboard", "/")
        ui.link("Analytics", "/analytics")
        ui.link("Upload File", "/upload")
        ui.link("About", "/about")
    uploaded = {"file": None, "name": None, "content": None, "type": None}
    columns = []
    mapping = {}

    def handle_upload(e):
        uploaded["file"] = e
        uploaded["name"] = e.name
        uploaded["content"] = e.content
        uploaded["type"] = e.type
        files = {"file": (e.name, e.content, e.type)}
        resp = requests.post(f"{API_BASE}/grades/upload/preview", files=files)
        if resp.status_code == 200:
            data = resp.json()
            nonlocal columns
            columns = data["columns"]
            ui.notify("File loaded. Map columns below.", type="positive")
        else:
            ui.notify("Preview failed", type="negative")

    ui.upload(on_upload=handle_upload, label="Upload CSV or Excel", auto_upload=True).classes("m-4")

    def validate_and_preview():
        if not uploaded["file"]:
            ui.notify("No file uploaded", type="warning")
            return
        files = {"file": (uploaded["name"], uploaded["content"], uploaded["type"])}
        resp = requests.post(f"{API_BASE}/grades/upload/validate", files=files, json=mapping)
        if resp.status_code == 200:
            result = resp.json()
            ui.notify(f"Valid rows: {result['valid_rows']}, errors: {len(result['errors'])}", type="positive")
            if result['errors']:
                with ui.dialog() as dialog, ui.card():
                    ui.label("Errors:")
                    for err in result['errors'][:10]:
                        ui.label(err)
                    ui.button("Close", on_click=dialog.close)
                dialog.open()
        else:
            ui.notify("Validation failed", type="negative")

    def insert_data():
        if not uploaded["file"]:
            ui.notify("No file", type="warning")
            return
        files = {"file": (uploaded["name"], uploaded["content"], uploaded["type"])}
        validate_resp = requests.post(f"{API_BASE}/grades/upload/validate", files=files, json=mapping)
        if validate_resp.status_code == 200:
            valid_data = validate_resp.json().get("data", [])
            if valid_data:
                insert_resp = requests.post(f"{API_BASE}/grades/upload/insert", json=valid_data)
                if insert_resp.status_code == 200:
                    ui.notify("Inserted successfully", type="positive")
                else:
                    ui.notify("Insert failed", type="negative")
            else:
                ui.notify("No valid rows to insert", type="warning")
        else:
            ui.notify("Validation failed", type="negative")

    with ui.card():
        ui.label("Map CSV/Excel columns to database fields")
        for field in ["student_name", "subject", "marks_obtained", "total_marks", "semester", "date", "exam_type", "father_name"]:
            if columns:
                ui.select(label=f"Column for {field}", options=columns, on_change=lambda e, f=field: mapping.update({f: e.value})).classes("w-full")
            else:
                ui.label(f"Upload file first to see columns for {field}")
        ui.button("Validate", on_click=validate_and_preview)
        ui.button("Insert to Database", on_click=insert_data)

def create_about():
    ui.page_title("About")
    with ui.header():
        ui.link("Dashboard", "/")
    with ui.left_drawer():
        ui.link("Dashboard", "/")
        ui.link("Analytics", "/analytics")
        ui.link("Upload File", "/upload")
        ui.link("About", "/about")
    ui.markdown("""
## GradePulse - Student Grade Tracker
**Developer:** AdnanRaza (ID: 0267)
**Assignment:** Level 2 Assignment 1
**Tech Stack:** FastAPI, SQLModel, NiceGUI, Groq, Pandas
**Features:** CRUD, AI Study Tips, CSV/Excel upload with column mapping, export to CSV/Excel, light/dark mode.
""")

def setup_frontend(app: FastAPI):
    ui.run_with(app)
    @ui.page("/")
    def dashboard():
        create_dashboard()
    @ui.page("/analytics")
    def analytics():
        create_analytics()
    @ui.page("/upload")
    def upload():
        create_upload_page()
    @ui.page("/about")
    def about():
        create_about()