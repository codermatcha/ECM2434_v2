FROM python:3.12-slim

WORKDIR /code

RUN apt-get update && apt-get install -y \
    gcc \
    python3-dev \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN python manage.py collectstatic --noinput

EXPOSE 8080

CMD ["gunicorn", "ECM2434_A_2_202425.wsgi:application", "--bind", "0.0.0.0:8080"]
