FROM python:3.8-slim-buster

ENV PYTHONUNBUFFERED=1

WORKDIR /app

RUN apt update \
    && apt install -y ffmpeg \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r ./requirements.txt

COPY soundbot.py /app/soundbot.py

CMD [ "python", "/app/soundbot.py" ]
