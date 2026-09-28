# The course requires Python 3.9; this legacy image is for the training lab only.
FROM python:3.9-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY service/ ./service/
RUN useradd --uid 1000 --no-create-home theia && chown -R theia /app
USER 1000

EXPOSE 8080
CMD ["gunicorn", "--bind=0.0.0.0:8080", "--log-level=info", "--access-logfile=-", "service:app"]
