############################
# BASE
############################
FROM python:3.14-slim AS base

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    ffmpeg \
    libsndfile1 \
    curl \
    && rm -rf /var/lib/apt/lists/*

############################
# DEPENDENCIES
############################
FROM base AS dependencies

COPY requirements.txt .
RUN pip install --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

############################
# DEV
############################
FROM dependencies AS dev

ENV DJANGO_SETTINGS_MODULE=vstweaker.settings.dev

COPY manage.py .
COPY vstweaker vstweaker
COPY manager manager
COPY mixer mixer

EXPOSE 8000
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]

############################
# BUILD (STATIC)
############################
FROM dev AS build

ENV DJANGO_SETTINGS_MODULE=vstweaker.settings.prod

RUN python manage.py collectstatic --noinput

############################
# PROD WEB
############################
FROM base AS prod

ENV DJANGO_SETTINGS_MODULE=vstweaker.settings.prod

RUN useradd -m django
USER django

COPY --from=dependencies /usr/local/lib/python3.14/site-packages /usr/local/lib/python3.14/site-packages
COPY --from=dependencies /usr/local/bin /usr/local/bin

COPY --from=build /app /app

EXPOSE 8000

CMD ["gunicorn", "vstweaker.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "3"]
