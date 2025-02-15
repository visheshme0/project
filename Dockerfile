FROM python:3.9-slim

# Install dependencies for Tesseract OCR
RUN apt-get update && apt-get install -y tesseract-ocr

# Set working directory
WORKDIR /app

# Copy requirements file and install dependencies
COPY requirements.txt /app/
RUN pip install -r requirements.txt

# Copy the rest of the application code
COPY . /app/

# Expose the API port
EXPOSE 8000

# Run the app
CMD ["python", "app.py"]

