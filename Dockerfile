FROM python:3.8-slim-buster

WORKDIR /app

RUN apt update \
    && apt install -y ffmpeg \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r ./requirements.txt

COPY . ./

CMD [ "python", "/app/soundbot.py" ]
