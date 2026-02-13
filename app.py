from flask import Flask, render_template, request
import os
import re
import base64
from io import BytesIO
import matplotlib.pyplot as plt
from PyPDF2 import PdfReader

app = Flask(__name__)

def extract_pdf_text(file):
    reader = PdfReader(file)
    text = ""
    for page in reader.pages:
        text += page.extract_text() or ""
    return text

def smart_structure(text):
    lines = [l.strip() for l in text.split("\n") if l.strip()]
    title = lines[0] if lines else "Generated Report"
    summary = " ".join(lines[:3])
    key_points = lines[3:8]
    details = lines[8:]
    return title, summary, key_points, details

def generate_chart(text):
    numbers = re.findall(r'\b\d+\b', text)
    numbers = [int(n) for n in numbers[:6]]
    if not numbers:
        return None

    fig = plt.figure()
    plt.bar(range(len(numbers)), numbers)
    plt.title("Auto Generated Chart")

    img = BytesIO()
    plt.savefig(img, format='png')
    img.seek(0)
    plt.close(fig)

    return base64.b64encode(img.getvalue()).decode()

@app.route("/", methods=["GET", "POST"])
def index():
    title = summary = ""
    key_points = details = []
    chart = None

    if request.method == "POST":
        file = request.files["file"]
        if file:
            text = extract_pdf_text(file)
            title, summary, key_points, details = smart_structure(text)
            chart = generate_chart(text)

    return render_template("index.html",
                           title=title,
                           summary=summary,
                           key_points=key_points,
                           details=details,
                           chart=chart)

if __name__ == "__main__":
    app.run()
