FROM python:3.10-slim

WORKDIR /app

# Prevent python from buffering console outputs
ENV PYTHONUNBUFFERED=1

# Added a space before the '.'
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Added a space before the '.'
COPY app.py .

# Starts the RAG interactive loop
CMD ["python", "app.py"]