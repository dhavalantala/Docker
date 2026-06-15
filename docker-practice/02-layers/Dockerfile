FROM python:3.11-slim
WORKDIR /app

# Coping everything FIRST -big mistake
COPY requirements.txt .

# Install dependencies - this layers gets CACHED
# as long as requirements.txt doesn't change
RUN pip install -r requirements.txt

COPY app.py .

CMD ["python", "app.py"]
