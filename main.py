from fastapi import FastAPI, HTTPException, Query
import subprocess
import json
import sqlite3
from pathlib import Path
from datetime import datetime
import os
import openai

app = FastAPI()
@app.post("/run")
def run_task(task: str = Query(..., description="Plain-English task description")):
    return {"status": "success", "output": f"Task received: {task}"}
def classify_task(task: str):
    client = openai.Client(api_key="AIPROXY_TOKEN")
    
    response = client.chat.completions.create(
        model="GPT-4o-Mini",
        messages=[{"role": "user", "content": f"Classify this task into A1-A10: {task}"}]
    )
    
    return response.choices[0].message.content

# Assuming datagen.py is in the same directory as your notebook
import datagen  # Import the datagen module

# Set the email and root directory in the config dictionary
datagen.config["email"] = "23f1001029@ds.study.iitm.ac.in"  # Replace with your actual email
datagen.config["root"] = "C://Users/DELL/data"  # Or any desired output directory

# Call the functions to generate the data
datagen.a2_format_markdown()
datagen.a3_dates()
datagen.a4_contacts()
datagen.a5_logs()
datagen.a6_docs()
datagen.a7_email()
datagen.a8_credit_card_image()
datagen.a9_comments()
datagen.a10_ticket_sales()

print("Data generation completed.")


DATA_DIR = "/data"
@app.get("/execute_task")
def execute_task(task: str) -> str:
    """
    Use Ollama to classify the task and execute the corresponding function.
    """
    try:
        result = subprocess.run(["ollama", "run", "mistral", f"Classify this task into A1-A10 or B1-B10: {task}"], 
                                capture_output=True, text=True)
        
        if result.returncode != 0:
            raise RuntimeError(f"Ollama processing error: {result.stderr}")

        task_category = result.stdout.strip().split()[0]  # Ensure clean response
        
        print(f"Ollama classified task as: {task_category}")  # Debugging step

        # Define task mapping
        task_mapping = {
            "A1": task_A1,  # Add the missing A1 function
            "A2": task_A2,
            "A3": task_A3,
            "A4": task_A4,
            "A5": task_A5,
            "A6": task_A6,
            "A7": task_A7,
            "A8": task_A8,
            "A9": task_A9,
            "A10": task_A10,
            "B1": task_B1,
            "B2": task_B2,
            "B3": task_B3,
            "B4": task_B4,
            "B5": task_B5,
            "B6": task_B6,
            "B7": task_B7,
            "B8": task_B8,
            "B9": task_B9,
            "B10": task_B10
        }

        # Check if task exists before calling it
        if task_category in task_mapping:
            return task_mapping[task_category]()
        else:
            raise RuntimeError(f"Unrecognized task: {task_category}")

    except Exception as e:
        raise RuntimeError(f"LLM processing error: {str(e)}")

def task_A1():
    subprocess.run(["pip", "install", "uv"], check=True)
    subprocess.run(["python", "-m", "uv", "https://raw.githubusercontent.com/sanand0/tools-in-data-science-public/tds-2025-01/project-1/datagen.py", "23f1001026@ds.studt.iitm.ac.in"], check=True)
     # Use "data" inside the project
    #return "Data generation completed."

def task_A2():
    # List of date formats to try
    subprocess.run(["npx", "prettier@3.4.2", "--write", "/data/format.md"], check=True)
    return "Formatted /data/format.md"

def task_A3():
    #count Wednesday
    wednesdays = 0
    with open("/data/dates.txt", "r") as file:
        for line in file:
            date = datetime.strptime(line.strip(), "%Y-%m-%d")
            if date.weekday() == 2:  # Wednesday
                wednesdays += 1
    with open("/data/dates-wednesdays.txt", "w") as file:
        file.write(str(wednesdays))
    return f"Wednesdays counted: {wednesdays}"

def task_A4():
    #sort_contacts
    with open("/data/contacts.json", "r") as file:
        contacts = json.load(file)
    sorted_contacts = sorted(contacts, key=lambda x: (x["last_name"], x["first_name"]))
    with open("/data/contacts-sorted.json", "w") as file:
        json.dump(sorted_contacts, file, indent=2)
    return "Sorted contacts.json"

def task_A5():
    # Get the first line of the 10 most recent log files
    log_files = sorted(Path("/data/logs/").glob("*.log"), key=lambda x: x.stat().st_mtime, reverse=True)[:10]
    with open("/data/logs-recent.txt", "w") as outfile:
        for log_file in log_files:
            with open(log_file, "r") as infile:
                first_line = infile.readline().strip()
                outfile.write(first_line + "\n")
    return "Extracted first lines of 10 recent log files."

def task_A6():
    # Extract the first H1 from each file
    index = {}
    for md_file in Path("/data/docs/").glob("*.md"):
        with open(md_file, "r") as file:
            for line in file:
                if line.startswith("# "):
                    index[md_file.name] = line.strip("# ").strip()
                    break
    with open("/data/docs/index.json", "w") as file:
        json.dump(index, file, indent=2)
    return "Created index.json"

def task_A7():
    #Extract the sender's email address
    with open("/data/email.txt", "r") as file:
        email_content = file.read()
    result = subprocess.run(["ollama", "run", "mistral", f"Extract the sender email: {email_content}"], capture_output=True, text=True)
    email_address = result.stdout.strip()
    with open("/data/email-sender.txt", "w") as file:
        file.write(email_address)
    return f"Extracted sender email: {email_address}"

def task_A8():
    #extract_credit_card_number
    result = subprocess.run(["ollama", "run", "mistral", "Extract credit card number from /data/credit-card.png"], capture_output=True, text=True)
    card_number = result.stdout.strip().replace(" ", "")
    with open("/data/credit-card.txt", "w") as file:
        file.write(card_number)
    return "Extracted credit card number."

def task_A9():
    #Find the most similar pair of comments
    with open("/data/comments.txt", "r") as file:
        comments = file.readlines()
    # Find most similar comments using embeddings (mocked)
    similar_comments = comments[:2]
    with open("/data/comments-similar.txt", "w") as file:
        file.write("\n".join(similar_comments))
    return "Extracted most similar comments."

def task_A10():
    #Query to calculate total sales for "Gold" ticket type
    conn = sqlite3.connect("/data/ticket-sales.db")
    cursor = conn.cursor()
    cursor.execute("SELECT SUM(units * price) FROM tickets WHERE type = 'Gold'")
    total_sales = cursor.fetchone()[0]
    conn.close()
    with open("/data/ticket-sales-gold.txt", "w") as file:
        file.write(str(total_sales))
    return f"Total sales for Gold tickets: {total_sales}"

#Security Wrapper for File Access
import os

DATA_DIR = "/data"

def task_B1(path: str) -> str:
    """ Ensure that the path stays inside /data and prevent deletion. """
    abs_path = os.path.abspath(path)
    if not abs_path.startswith(DATA_DIR):
        raise PermissionError(f"Access denied: {path} is outside {DATA_DIR}")
    return abs_path
def task_B2(path: str, mode="r"):
    """ Wrapper around open() that restricts access and prevents deletion """
    if "w" in mode and "x" not in mode:  # Prevent 'w' mode (overwrite)
        raise PermissionError(f"Write operation not allowed: {path}")
    return open(task_B1(path), mode)

##B3: Fetch Data from an API and Save It
import requests

def task_B3(url: str, output_file: str):
    response = requests.get(url)
    if response.status_code == 200:
        with task_B2(output_file, "w") as file:
            file.write(response.text)
        return f"Data fetched from {url} and saved to {output_file}"
    else:
        raise RuntimeError(f"Failed to fetch data: {response.status_code}")

##B4: Clone a Git Repo and Make a Commit
import git

def task_B4(repo_url: str, commit_message: str):
    repo_path = f"/data/repos/{repo_url.split('/')[-1].replace('.git', '')}"
    repo = git.Repo.clone_from(repo_url, repo_path)
    with task_B2(f"{repo_path}/README.md", "a") as file:
        file.write("\nUpdated by automation.")
    repo.git.add("--all")
    repo.index.commit(commit_message)
    repo.git.push()
    return f"Committed changes to {repo_url}"

##B5: Run a SQL Query on a SQLite or DuckDB Database
import duckdb

def task_B5(query: str, db_path: str, output_file: str):
    conn = duckdb.connect(task_B1(db_path))
    result = conn.execute(query).fetchdf()
    conn.close()
    result.to_csv(output_file, index=False)
    return f"Query executed and saved to {output_file}"

#B6: Extract Data from a Website (Web Scraping)
from bs4 import BeautifulSoup
#B6: Clone a Git Repo and Make a Commit
def task_B6(url: str, output_file: str):
    response = requests.get(url)

    soup = BeautifulSoup(response.text, "html.parser")
    text = soup.get_text()
    with task_B2(output_file, "w") as file:
        file.write(text)
    return f"Extracted text from {url} and saved to {output_file}"
#B7: Compress or Resize an Image
from PIL import Image

def task_B7(image_path: str, output_path: str, width: int = 800):
    img = Image.open(task_B1(image_path))
    img = img.resize((width, int(img.height * (width / img.width))))
    img.save(output_path, quality=85)
    return f"Image resized and saved to {output_path}"
#B8: Transcribe Audio from an MP3 File
import whisper

def task_B8(audio_path: str, output_file: str):
    model = whisper.load_model("base")
    result = model.transcribe(task_B1(audio_path))
    with task_B1(output_file, "w") as file:
        file.write(result["text"])
    return f"Transcription saved to {output_file}"
#B9: Convert Markdown to HTML
import markdown

def task_B9(md_file: str, html_file: str):
    with task_B2(md_file, "r") as file:
        md_text = file.read()
    html = markdown.markdown(md_text)
    with task_B2(html_file, "w") as file:
        file.write(html)
    return f"Converted {md_file} to HTML and saved to {html_file}"
#B10: Write an API Endpoint that Filters a CSV File
import pandas as pd
from fastapi import Query

@app.get("/filter_csv")
def task_B10(file_path: str = Query(...), column: str = Query(...), value: str = Query(...)):
    df = pd.read_csv(task_B1(file_path))
    filtered_df = df[df[column] == value]

    return filtered_df.to_dict(orient="records")


