FROM python:3.8

WORKDIR /home

ENV TELEGRAM_API_TOKEN="1073786035:AAHVEc9fimGKWASp8WJngQFfzEKBWpeFZl8"
ENV TELEGRAM_PROXY_URL="http://193.232.150.42:3128"

ENV TZ=Europe/Moscow
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

RUN pip install -U pip aiogram pytz && apt-get update && apt-get install sqlite3
COPY *.py ./
COPY createdb.sql ./

ENTRYPOINT ["python", "bablo_bot.py"]
