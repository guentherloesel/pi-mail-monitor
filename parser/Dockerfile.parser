FROM python:3.11-slim

COPY ./parser/emailParser.py /app/emailParser.py

WORKDIR /app

RUN pip install couchdb

CMD ["python", "emailParser.py"]