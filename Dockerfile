FROM python:3.11-alpine

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1


WORKDIR /app

# Copying requirements first to leverage Docker cache
COPY requirements.txt .
RUN python -m pip install --upgrade pip
RUN pip install -r requirements.txt

# Create necessary log directory
RUN mkdir -p /app/logs

# Copy the rest of the application
COPY . .

CMD ["daphne", "backend.asgi:application"]
