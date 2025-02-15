# Use a lightweight Python image
#FROM python:3.11-slim
FROM node:18-bullseye as node
FROM python:3.9

# Install system dependencies
RUN apt-get update && apt-get install -y git curl \
ffmpeg \
libsndfile1 \&& rm -rf /var/lib/apt/lists/*

RUN npm install -g prettier@3.4.2

RUN apt-get update && apt-get install -y tesseract-ocr

RUN apt-get update && apt-get install -y sqlite3

# Install Ollama (for LLM processing)
#RUN curl -fsSL https://ollama.ai/install.sh | sh

# Set the working directory inside the container
WORKDIR /app

# Copy project files into the container
COPY . .

COPY requirements.txt .
RUN pip install --no-cache-dir-r requirements.txt

RUN mkdir -p /data

ARG AIPROXY_TOKEN
ENV AIPROXY_TOKEN={$AIPROXY_TOKEN}
ENV PIP_ROOT_USER_ACTION=ignore

# Expose FastAPI port
EXPOSE 8000

# Command to start FastAPI app
CMD ["uvicorn", "main:app", "--host", "127.0.0.1", "--port", "8000"]
