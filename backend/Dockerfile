FROM python:3.10-slim
WORKDIR /app

# Копируем из текущего контекста (папки backend)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копируем содержимое папки app
COPY ./app ./app

ENV PYTHONPATH=/app
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]