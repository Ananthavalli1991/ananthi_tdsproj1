# Use a lightweight Python image
FROM python:3.11-slim

# Install system dependencies
RUN apt-get update && apt-get install -y git curl && rm -rf /var/lib/apt/lists/*

# Install Ollama (for LLM processing)
RUN curl -fsSL https://ollama.ai/install.sh | sh

# Set the working directory inside the container
WORKDIR /app

# Copy project files into the container
COPY . .

# Install Python dependencies
#RUN pip install --no-cache-dir -r requirements.txt

# Expose FastAPI port
EXPOSE 8000

# Command to start FastAPI app
CMD ["uvicorn", "main:app", "--host", "127.0.0.1", "--port", "8000"]
