# Base image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install python-multipart  # needed for file uploads

# Copy all project files
COPY . .

# Expose FastAPI port
EXPOSE 8000

# Set environment variables (optional, can also use --env-file when running)
# ENV SUPABASE_URL=your_supabase_url
# ENV SUPABASE_KEY=your_supabase_key
# ENV WEAVIATE_URL=your_weaviate_url
# ENV WEAVIATE_API_KEY=your_weaviate_api_key
# ENV OPENAI_API_KEY=your_openai_key

# Run FastAPI with Uvicorn
CMD ["uvicorn", "backend.app:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
