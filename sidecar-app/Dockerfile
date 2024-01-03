FROM python:3.8-slim

WORKDIR /app
COPY . /app

RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 5001

ENV SERVICE_NAME default_service

CMD ["python", "app.py"]
