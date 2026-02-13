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


def extract_vacancy_data(text):
    vacancy_data = {}

    lines = text.split("\n")
    current_zone = None
    current_category = None

    for line in lines:
        line = line.strip()

        # Detect Zone (Example: SECR, SCR etc.)
        if re.match(r'^[A-Z]{2,5}$', line):
            current_zone = line
            vacancy_data[current_zone] = {}

        # Detect Category
        elif line in ["UR", "OBC", "SC", "ST", "EWS"]:
            current_category = line
            if current_zone:
                vacancy_data[current_zone][current_category] = {}

        # Detect Post + Vacancy (Example: Pointsman B 147)
        else:
            match = re.match(r'(.+?)\s+(\d+)$', line)
            if match and current_zone and current_category:
                post = match.group(1)
                count = int(match.group(2))
                vacancy_data[current_zone][current_category][post] = count

    return vacancy_data

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
    vacancy_data = {}

    if request.method == "POST":
        file = request.files["file"]
        if file:
            text = extract_pdf_text(file)

            title, summary, key_points, details = smart_structure(text)
            chart = generate_chart(text)

            vacancy_data = extract_vacancy_data(text)

    return render_template("index.html",
                           title=title,
                           summary=summary,
                           key_points=key_points,
                           details=details,
                           chart=chart,
                           vacancy_data=vacancy_data)


if __name__ == "__main__":
    app.run()
