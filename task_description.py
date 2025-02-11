import os
import subprocess
import datetime
import json
import sqlite3
from transformers import pipeline
#tasks definition
# Initialize the LLM
llm = pipeline('text-generation', model='gpt-3')

def install_and_run_script(email):
    subprocess.run(["pip", "install", "uv"])
    subprocess.run(["python", "https://raw.githubusercontent.com/sanand0/tools-in-data-science-public/tds-2025-01/project-1/datagen.py", email])

def format_md_file():
    subprocess.run(["npx", "prettier@3.4.2", "--write", "/data/format.md"])

def count_wednesdays():
    with open('/data/dates.txt', 'r') as f:
        dates = f.readlines()
    wednesdays = sum(1 for date in dates if datetime.datetime.strptime(date.strip(), '%Y-%m-%d').weekday() == 2)
    with open('/data/dates-wednesdays.txt', 'w') as f:
        f.write(str(wednesdays))

def sort_contacts():
    with open('/data/contacts.json', 'r') as f:
        contacts = json.load(f)
    sorted_contacts = sorted(contacts, key=lambda x: (x['last_name'], x['first_name']))
    with open('/data/contacts-sorted.json', 'w') as f:
        json.dump(sorted_contacts, f, indent=4)

def write_recent_logs():
    log_files = sorted([f for f in os.listdir('/data/logs') if f.endswith('.log')], key=lambda x: os.path.getmtime(os.path.join('/data/logs', x)), reverse=True)
    recent_logs = []
    for log_file in log_files[:10]:
        with open(f'/data/logs/{log_file}', 'r') as f:
            recent_logs.append(f.readline().strip())
    with open('/data/logs-recent.txt', 'w') as f:
        f.writelines('\n'.join(recent_logs))

def create_docs_index():
    index = {}
    for root, dirs, files in os.walk('/data/docs'):
        for file in files:
            if file.endswith('.md'):
                with open(os.path.join(root, file), 'r') as f:
                    for line in f:
                        if line.startswith('# '):
                            index[file] = line[2:].strip()
                            break
    with open('/data/docs/index.json', 'w') as f:
        json.dump(index, f, indent=4)

def extract_email_sender():
    with open('/data/email.txt', 'r') as f:
        email_content = f.read()
    prompt = f"Extract the sender's email address from the following content:\n{email_content}"
    result = llm(prompt, max_length=50)
    email_address = result[0]['generated_text'].strip()
    with open('/data/email-sender.txt', 'w') as f:
        f.write(email_address)

def extract_credit_card_number():
    # Assume we have an OCR function to extract text from image
    card_number = ocr_extract_text('/data/credit-card.png').replace(' ', '')
    with open('/data/credit-card.txt', 'w') as f:
        f.write(card_number)

def find_similar_comments():
    with open('/data/comments.txt', 'r') as f:
        comments = f.readlines()
    # Assume we have a function to calculate embeddings and find similar pairs
    comment1, comment2 = find_most_similar_pair(comments)
    with open('/data/comments-similar.txt', 'w') as f:
        f.writelines([comment1, comment2])

def calculate_ticket_sales():
    conn = sqlite3.connect('/data/ticket-sales.db')
    cursor = conn.cursor()
    cursor.execute("SELECT SUM(units * price) FROM tickets WHERE type = 'Gold'")
    total_sales = cursor.fetchone()[0]
    conn.close()
    with open('/data/ticket-sales-gold.txt', 'w') as f:
        f.write(str(total_sales))
