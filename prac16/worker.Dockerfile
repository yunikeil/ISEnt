FROM python:3.11-alpine

WORKDIR /authprac

COPY requirements.txt ./

RUN pip install --no-cache-dir -r requirements.txt

COPY ./ /authprac/
