# Use official Python image
FROM python:3.9-slim

# Set working directory
WORKDIR /app

# Install system dependencies (Tesseract OCR + others)
RUN apt-get update && apt-get install -y \
    tesseract-ocr \
    libtesseract-dev \
    poppler-utils \
    && rm -rf /var/lib/apt/lists/*

RUN pip install torch==2.2.1+cpu torchaudio==2.2.1+cpu torchvision==0.17.1+cpu\
    -f https://download.pytorch.org/whl/torch_stable.html 

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --no-deps -r requirements.txt


# Copy the entire app
COPY . .

# Expose FastAPI port
EXPOSE 8000

# Run FastAPI with uvicorn
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
