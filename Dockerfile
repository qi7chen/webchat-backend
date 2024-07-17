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

CMD bash -c "gunicorn -b 0.0.0.0:80 backend.wsgi:application"
