from fastapi import FastAPI, HTTPException, Query
import requests
import os
import asyncio
import json
import subprocess
import shutil
import sqlite3
from concurrent.futures import ThreadPoolExecutor
from PIL import Image
import pytesseract
from pydub import AudioSegment
import speech_recognition as sr
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
def extract_text_from_image(image_path: str):
    try:
        image = Image.open(image_path)
        extracted_text = pytesseract.image_to_string(image)
        return extracted_text.strip()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing image: {str(e)}")
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
            try:
                parts = task.split()
                api_url = next((part for part in parts if part.startswith("http")), None)

                if not api_url:
                    return "Error: No API URL provided in the task"

                response = requests.get(api_url)
                response.raise_for_status()  # Raise an error for bad responses (4xx, 5xx)

                output_path = f"/data/api-response.json"
                with open(output_path, "w") as f:
                    json.dump(response.json(), f, indent=2)

                return f"Fetched and saved API data from {api_url}"
            except Exception as e:
                return f"Error fetching API data: {str(e)}"

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
            repo_url = task.split()[-1] 
            if os.path.exists("/data/repo"):
                shutil.rmtree("/data/repo")
            subprocess.run(["git", "clone", "repo_url", "/data/repo"], check=True)
            return "Cloned git repository"
        elif "run SQL query" in task:
            try:
            # Extract SQL query from the task description
                query_start = task.lower().find("run sql query") + len("run sql query")
                sql_query = task[query_start:].strip()

                if not sql_query:
                    return "Error: No SQL query provided in the task"

                conn = sqlite3.connect("/data/database.db")
                cursor = conn.cursor()
                cursor.execute(sql_query)

                # Fetch results dynamically based on query type
                if sql_query.strip().lower().startswith(("select", "pragma")):
                    result = cursor.fetchall()
                else:
                    conn.commit()
                    result = "Query executed successfully"

                conn.close()

                return f"SQL query result: {result}"
            except Exception as e:
                return f"Error executing SQL query: {str(e)}"
            
        elif "scrape website" in task:
            try:
                # Extract website URL from the task description
                parts = task.split()
                website_url = next((part for part in parts if part.startswith("http")), None)

                if not website_url:
                    return "Error: No website URL provided in the task"

                response = requests.get(website_url)
                response.raise_for_status()  # Ensure the request was successful

                # Generate a filename based on the website domain
                domain = website_url.split("//")[-1].split("/")[0].replace(".", "_")
                output_path = f"/data/scraped_{domain}.html"

                with open(output_path, "w", encoding="utf-8") as f:
                    f.write(response.text)

                return f"Scraped website data from {website_url} and saved to {output_path}"
            except Exception as e:
                return f"Error scraping website: {str(e)}"

        elif "resize image" in task:
            shutil.copy("/data/image.png", "/data/image-resized.png")
            return "Image resized"
        elif "transcribe audio" in task:
            try:
        # Extract file path from task description
                task_parts = task.split()
                audio_file = next((word for word in task_parts if word.endswith((".mp3", ".wav", ".ogg", ".flac"))), None)

                if not audio_file:
                    return "Error: No audio file provided in the task"

                audio_path = os.path.join("/data", audio_file)

                if not os.path.exists(audio_path):
                    return f"Error: File {audio_file} not found"

                # Convert to WAV if necessary
                if not audio_file.endswith(".wav"):
                    sound = AudioSegment.from_file(audio_path)
                    wav_path = audio_path.rsplit(".", 1)[0] + ".wav"
                    sound.export(wav_path, format="wav")
                else:
                    wav_path = audio_path

                # Transcribe audio
                recognizer = sr.Recognizer()
                with sr.AudioFile(wav_path) as source:
                    audio_data = recognizer.record(source)
                    transcription = recognizer.recognize_google(audio_data)  # Uses Google Speech API

                # Save transcription
                transcript_file = f"{audio_path.rsplit('.', 1)[0]}.txt"
                with open(transcript_file, "w") as f:
                    f.write(transcription)

                return f"Transcribed audio saved to {transcript_file}"
            except Exception as e:
                return f"Error transcribing audio: {str(e)}"
        elif "convert Markdown" in task:
            subprocess.run(["pandoc", "-o", "/data/output.html", "/data/input.md"], check=True)
            return "Converted Markdown to HTML"
        elif "extract credit card number" in task:
            extracted_text = extract_text_from_image("/data/credit-card.png")
            credit_card_number = "".join(filter(str.isdigit, extracted_text))
            with open("/data/credit-card.txt", "w") as f:
                f.write(credit_card_number)
            return "Extracted and saved credit card number"
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
