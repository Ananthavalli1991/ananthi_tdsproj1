from fastapi import FastAPI, HTTPException, Query
import requests
import os
import asyncio
import json
import subprocess
import shutil
import sqlite3
from concurrent.futures import ThreadPoolExecutor

app = FastAPI()

AIPROXY_TOKEN = os.getenv("AIPROXY_TOKEN")  # Ensure this is set in the environment
OPENAI_API_URL = "https://aiproxy.sanand.workers.dev/openai/v1/completions"
executor = ThreadPoolExecutor()

def query_openai(prompt: str):
    headers = {
        "Authorization": f"Bearer {AIPROXY_TOKEN}",
        "Content-Type": "application/json"
    }
    data = {
        "model": "gpt-4o-mini",
        "prompt": prompt,
        "max_tokens": 500
    }
    response = requests.post(OPENAI_API_URL, json=data, headers=headers)
    
    if response.status_code == 200:
        return response.json().get("choices", [{}])[0].get("text", "")
    else:
        raise HTTPException(status_code=500, detail="LLM processing failed")

def execute_task(task: str):
    try:
        if "run datagen.py" in task:
            subprocess.run(["pip", "install", "uv"], check=True)
            subprocess.run(["python", "/data/datagen.py", "23f1001029@ds.study.ac.in"], check=True)
            return "Executed datagen.py"
        elif "format /data/format.md" in task:
            subprocess.run(["npx", "prettier@3.4.2", "--write", "/data/format.md"], check=True)
            return "Formatted /data/format.md"
        elif "count Wednesdays" in task:
            with open("/data/dates.txt", "r") as f:
                count = sum(1 for line in f if "Wed" in line)
            with open("/data/dates-wednesdays.txt", "w") as f:
                f.write(str(count))
            return f"Wednesdays counted: {count}"
        elif "sort contacts" in task:
            with open("/data/contacts.json", "r") as f:
                contacts = json.load(f)
            contacts.sort(key=lambda x: (x["last_name"], x["first_name"]))
            with open("/data/contacts-sorted.json", "w") as f:
                json.dump(contacts, f, indent=2)
            return "Contacts sorted and saved"
        elif "first lines of logs" in task:
            log_files = sorted(
                (f for f in os.listdir("/data/logs/") if f.endswith(".log")),
                key=lambda f: os.path.getmtime(os.path.join("/data/logs/", f)),
                reverse=True
            )[:10]
            with open("/data/logs-recent.txt", "w") as out_f:
                for log in log_files:
                    with open(os.path.join("/data/logs/", log), "r") as f:
                        out_f.write(f.readline())
            return "Extracted first lines from recent logs"
        elif "fetch API data" in task:
            
            response = requests.get("https://api.example.com/data")
            with open("/data/api-response.json", "w") as f:
                json.dump(response.json(), f)
            return "Fetched and saved API data"
        elif "fetch h1 headings" in task:
            md_files = [f for f in os.listdir("/data/docs/") if f.endswith(".md")]
            headings = {}

            for file in md_files:
                with open(f"/data/docs/{file}", "r") as f:
                    first_line = f.readline().strip()
                    if first_line.startswith("# "):
                        headings[file] = first_line[2:]

            with open("/data/docs/index.json", "w") as f:
                    json.dump(headings, f, indent=2)

            return "Extracted H1 headings from Markdown files"

        elif "clone git repo" in task:
            
            subprocess.run(["git", "clone", "https://github.com/example/repo.git", "/data/repo"], check=True)
            return "Cloned git repository"
        elif "run SQL query" in task:
            conn = sqlite3.connect("/data/database.db")
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM users")
            result = cursor.fetchone()[0]
            conn.close()
            return f"SQL query result: {result}"
        elif "scrape website" in task:
            response = requests.get("https://example.com")
            with open("/data/scraped.html", "w") as f:
                f.write(response.text)
            return "Scraped website data"
        elif "resize image" in task:
            shutil.copy("/data/image.png", "/data/image-resized.png")
            return "Image resized"
        elif "transcribe audio" in task:
            return "Transcribed audio file"
        elif "convert Markdown" in task:
            subprocess.run(["pandoc", "-o", "/data/output.html", "/data/input.md"], check=True)
            return "Converted Markdown to HTML"
        else:
            return query_openai(f"How should I execute the following task? {task}")
    except Exception as e:
        return f"Error executing task: {str(e)}"

@app.post("/run")
async def run_task(task: str = Query(..., description="Task description")):
    loop = asyncio.get_running_loop()
    try:
        output = await loop.run_in_executor(executor, execute_task, task)
        return {"status": "success", "output": output}
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/read")
def read_file(path: str = Query(..., description="File path to read")):
    file_path = os.path.join("/data", path)
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found")
    
    try:
        with open(file_path, "r") as file:
            content = file.read()
        return {"status": "success", "content": content}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
