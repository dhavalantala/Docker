FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY app.py .

# Document which port this container listens on
# EXPOSE doesn't actually open the port — it's documentation
EXPOSE 5000

CMD ["python", "app.py"]
