FROM python:3.10.9-slim

WORKDIR /ugc_api
COPY requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt --no-cache-dir
COPY . .
CMD ["python", "-m", "gunicorn", "main:app", "-k", "uvicorn.workers.UvicornH11Worker", "--bind", "0.0.0.0:8000", "--workers", "4"]