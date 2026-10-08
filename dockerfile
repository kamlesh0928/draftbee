FROM python:3.13-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --non-cache-dir -r requirements.txt

COPY . .

CMD ["python", "app/run_bot.py"]