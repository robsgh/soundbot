FROM python:3

WORKDIR /app

RUN apt update && apt install -y ffmpeg

COPY requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r ./requirements.txt

COPY ./soundboard ./soundboard
COPY . ./

CMD [ "python", "/app/soundbot.py" ]
