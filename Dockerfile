FROM python:3.12-slim-bookworm

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY main.py config.py .env ./

# -u — сразу видеть логи в docker logs
CMD ["python", "-u", "main.py"]
