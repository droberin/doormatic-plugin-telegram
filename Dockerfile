FROM python:3-slim

RUN mkdir -p /app/scripts
RUN mkdir -p /app/config

COPY requirements.txt /app/scripts/requirements.txt
COPY config.json.example /app/config/config.json.example

WORKDIR /app/scripts

RUN pip3 install -r requirements.txt

COPY telegram_bot.py /app/scripts/telegram_bot.py

CMD [ "python", "telegram_bot.py" ]
