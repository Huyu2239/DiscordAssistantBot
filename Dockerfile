FROM python:3.12.5-bullseye

RUN apt update; apt -y install tzdata && \
cp /usr/share/zoneinfo/Asia/Tokyo /etc/localtime

RUN apt update
RUN apt -yV upgrade

RUN pip install -U pip==24.2

WORKDIR /src

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY src/. .
COPY .env .

CMD ["python", "-u", "main.py"]
