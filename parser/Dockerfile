FROM python:3.11-slim

COPY emailParser.py /app/emailParser.py

WORKDIR /app

RUN pip install nats-py python-dotenv

CMD ["python", "emailParser.py"]