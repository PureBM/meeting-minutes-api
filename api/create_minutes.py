from flask import Flask, request, jsonify
from datetime import date
import csv, io, base64, os
from docx import Document

app = Flask(__name__)

@app.post("/api/create_minutes")
def create_minutes():
    data = request.get_json()
    minutes_text = data.get("minutes", "")
    actions = data.get("actions", [])
    title = data.get("title", "Meeting")

    # Template path inside the deployed Vercel environment
    template_path = os.path.join(os.path.dirname(__file__), "Minutes_Template.dotx")

    if os.path.exists(template_path):
        doc = Document(template_path)
    else:
        doc = Document()
        doc.add_paragraph("(Template missing – using default layout)")

    doc.add_heading(f"{title} – {date.today()}", 0)
    doc.add_paragraph(minutes_text)

    # Word file
    word_stream = io.BytesIO()
    doc.save(word_stream)
    word_b64 = base64.b64encode(word_stream.getvalue()).decode("utf-8")

    # CSV file
    csv_stream = io.StringIO()
    writer = csv.writer(csv_stream)
    writer.writerow(["Action Agreed in Detail", "Owner", "Due Date"])
    for a in actions:
        writer.writerow([
            a.get("detail", ""), a.get("owner", ""), a.get("due", "")
        ])
    csv_b64 = base64.b64encode(csv_stream.getvalue().encode("utf-8")).decode("utf-8")

    return jsonify({"minutes_file": word_b64, "actions_file": csv_b64})
