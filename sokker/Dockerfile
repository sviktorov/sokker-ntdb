ARG PYTHON_VERSION=3.11-slim-bullseye

FROM python:${PYTHON_VERSION}

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# install psycopg2 dependencies.
# Install build tools and psycopg2 dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    gcc \
    libpq-dev \
    libcairo2-dev \
    pkg-config \
    python3-dev \
    libpango1.0-dev \
    libgdk-pixbuf2.0-dev \
    shared-mime-info \
    && rm -rf /var/lib/apt/lists/*

RUN mkdir -p /code

WORKDIR /code


COPY ./requirements.txt /code/
# Upgrade pip + install wheel early to avoid build failures
RUN pip install --upgrade pip setuptools wheel

RUN pip install -r requirements.txt
COPY . /code

EXPOSE 8000
#CMD ["/bin/bash", "-c", "python manage.py collectstatic --noinput"]
#CMD ["gunicorn", "--bind", ":8000", "--workers", "1", "sokker.wsgi"]
CMD ["/bin/bash", "-c", "python manage.py collectstatic --noinput && gunicorn --bind :8000 --workers 4 --timeout=600 --log-level debug sokker.wsgi"]
