import os
import subprocess
import json
from flask import Flask, request, jsonify
import requests
import sqlite3
from datetime import datetime
import markdown
import shutil
from PIL import Image
import pytesseract

app = Flask(__name__)

# Helper Functions
def install_uv():
    try:
        subprocess.check_call([os.sys.executable, "-m", "pip", "install", "uv"])
    except subprocess.CalledProcessError as e:
        return f"Error installing uv: {str(e)}"

def run_datagen(user_email):
    url = "https://raw.githubusercontent.com/sanand0/tools-in-data-science-public/tds-2025-01/project-1/datagen.py"
    try:
        response = requests.get(url, params={"email": user_email})
        with open("/data/generated_data.txt", "w") as file:
            file.write(response.text)
        return "Data generated successfully"
    except Exception as e:
        return f"Error running datagen.py: {str(e)}"

def format_file(file_path, prettier_version="3.4.2"):
    try:
        subprocess.check_call(["npx", f"prettier@{prettier_version}", "--write", file_path])
        return "File formatted successfully"
    except subprocess.CalledProcessError as e:
        return f"Error formatting file: {str(e)}"

def count_wednesdays(input_file, output_file):
    with open(input_file, "r") as f:
        dates = f.readlines()

    wednesday_count = sum(1 for date in dates if datetime.strptime(date.strip(), "%Y-%m-%d").weekday() == 2)
    
    with open(output_file, "w") as f:
        f.write(str(wednesday_count))

    return "Wednesdays counted successfully"

def sort_contacts(input_file, output_file):
    with open(input_file, "r") as f:
        contacts = json.load(f)

    sorted_contacts = sorted(contacts, key=lambda x: (x["last_name"], x["first_name"]))

    with open(output_file, "w") as f:
        json.dump(sorted_contacts, f)

    return "Contacts sorted successfully"

def write_log_first_line(log_dir, output_file):
    logs = sorted([os.path.join(log_dir, f) for f in os.listdir(log_dir) if f.endswith('.log')], reverse=True)
    with open(output_file, "w") as f:
        with open(logs[0], "r") as log_file:
            f.write(log_file.readline().strip())

    return "First line of most recent log written"

def extract_h1_from_md(docs_dir, output_file):
    index = {}
    for root, _, files in os.walk(docs_dir):
        for file in files:
            if file.endswith(".md"):
                file_path = os.path.join(root, file)
                with open(file_path, "r") as f:
                    content = f.read()
                    # Extract first H1 header
                    lines = content.splitlines()
                    for line in lines:
                        if line.startswith("# "):
                            index[file] = line[2:]  # Title without '#'
                            break

    with open(output_file, "w") as f:
        json.dump(index, f)

    return "H1 headers extracted successfully"

def extract_email_from_text(input_file, output_file):
    with open(input_file, "r") as f:
        email_text = f.read()
    
    # Simulate LLM for email extraction
    email = email_text.split('From: ')[1].split()[0]

    with open(output_file, "w") as f:
        f.write(email)

    return "Email address extracted successfully"

def extract_card_number_from_image(input_file, output_file):
    image = Image.open(input_file)
    card_number = pytesseract.image_to_string(image)
    
    # Clean card number
    card_number = "".join(card_number.split())
    
    with open(output_file, "w") as f:
        f.write(card_number)

    return "Card number extracted successfully"

def find_similar_comments(input_file, output_file):
    with open(input_file, "r") as f:
        comments = f.readlines()

    # Simulate comment similarity using a simple approach
    most_similar = None
    max_similarity = -1
    for i in range(len(comments)):
        for j in range(i + 1, len(comments)):
            similarity = compute_similarity(comments[i], comments[j])  # Placeholder similarity function
            if similarity > max_similarity:
                most_similar = (comments[i], comments[j])
                max_similarity = similarity

    with open(output_file, "w") as f:
        f.write(most_similar[0].strip() + "\n" + most_similar[1].strip())

    return "Most similar comments found successfully"

def compute_similarity(comment1, comment2):
    return len(set(comment1.split()) & set(comment2.split()))  # Simple similarity measure

def query_sales_db(input_db, output_file):
    conn = sqlite3.connect(input_db)
    cursor = conn.cursor()
    cursor.execute("SELECT SUM(units * price) FROM tickets WHERE type = 'Gold'")
    total_sales = cursor.fetchone()[0]
    conn.close()

    with open(output_file, "w") as f:
        f.write(str(total_sales))

    return "Gold ticket sales calculated successfully"
@app.route('/')
def home():
    return 'Welcome to the Task Agent API!'
# API Endpoints
@app.route('/run', methods=['POST'])
def run_task():
    task_description = request.args.get("task")
    try:
        if "Install uv" in task_description:
            install_uv()
            return jsonify(message="uv installed successfully"), 200
        elif "run datagen.py" in task_description:
            user_email = task_description.split("${user.email}")[1].strip()
            run_datagen(user_email)
            return jsonify(message="Data generation successful"), 200
        elif "Format" in task_description:
            file_path = "/data/format.md"
            format_file(file_path)
            return jsonify(message="File formatted successfully"), 200
        elif "count Wednesdays" in task_description:
            count_wednesdays("/data/dates.txt", "/data/dates-wednesdays.txt")
            return jsonify(message="Wednesdays counted successfully"), 200
        elif "sort contacts" in task_description:
            sort_contacts("/data/contacts.json", "/data/contacts-sorted.json")
            return jsonify(message="Contacts sorted successfully"), 200
        elif "write first line of log" in task_description:
            write_log_first_line("/data/logs", "/data/logs-recent.txt")
            return jsonify(message="First line written to logs-recent.txt"), 200
        elif "extract H1" in task_description:
            extract_h1_from_md("/data/docs", "/data/docs/index.json")
            return jsonify(message="H1 headers extracted successfully"), 200
        elif "extract email" in task_description:
            extract_email_from_text("/data/email.txt", "/data/email-sender.txt")
            return jsonify(message="Email extracted successfully"), 200
        elif "extract card number" in task_description:
            extract_card_number_from_image("/data/credit-card.png", "/data/credit-card.txt")
            return jsonify(message="Card number extracted successfully"), 200
        elif "find similar comments" in task_description:
            find_similar_comments("/data/comments.txt", "/data/comments-similar.txt")
            return jsonify(message="Similar comments found successfully"), 200
        elif "query ticket sales" in task_description:
            query_sales_db("/data/ticket-sales.db", "/data/ticket-sales-gold.txt")
            return jsonify(message="Ticket sales calculated successfully"), 200
        else:
            return jsonify(message="Unknown task description"), 400
    except Exception as e:
        return jsonify(message=str(e)), 500


@app.route('/read', methods=['GET'])
def read_file():
    file_path = request.args.get("path")
    if os.path.exists(file_path):
        with open(file_path, "r") as f:
            return jsonify(content=f.read()), 200
    else:
        return jsonify(message="File not found"), 404


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8000)
