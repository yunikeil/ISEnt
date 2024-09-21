FROM python:3.12.4-alpine3.20

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

WORKDIR /authprac

COPY requirements.txt ./
RUN pip install --upgrade pip && pip install --no-cache-dir -r requirements.txt

#COPY ./src /authprac/src
#COPY alembic.ini ./
#COPY .env ./
