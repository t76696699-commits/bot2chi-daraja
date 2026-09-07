FROM python:3.10-slim

WORKDIR /app

# Talab qilinadigan paketlarni o'rnatish
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Graceful shutdown signallari to'g'ri yetib borishi uchun
CMD ["python", "main.py"]