FROM python:3.10-slim

WORKDIR /app

RUN apt-get update && apt-get install -y build-essential cmake libboost-all-dev libpq-dev && \
    pip install --no-cache-dir -r requirements.txt && \
    apt-get remove -y build-essential cmake && \
    apt-get autoremove -y && \
    rm -rf /var/lib/apt/lists/*

COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

COPY . /app/

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

EXPOSE 8000

CMD ["sh", "-c", "python manage.py migrate && daphne -b 0.0.0.0 -p 8000 NOGA.asgi:application"]
