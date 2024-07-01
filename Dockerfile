FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1


WORKDIR /app

# Copying requirements first to leverage Docker cache
COPY requirements.txt .

RUN pip install -r requirements.txt

# Copy the rest of the application
COPY . .

# Create necessary log directory
RUN mkdir -p /app/logs

CMD bash -c "uvicorn --host=0.0.0.0 --port=80 backend.asgi:application"
