# Use an official Python runtime as a parent image
FROM python:3.8-slim

WORKDIR /app

COPY . /app
COPY k8s/hosts.txt /app/hosts.txt

RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 5000

CMD ["python", "app.py"]

