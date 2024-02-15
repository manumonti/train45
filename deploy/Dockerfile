FROM python:3.12-slim

RUN apt-get update && apt-get install -y cron python3 python3-pip

WORKDIR /app

COPY ../ /app

RUN pip3 install --no-cache-dir -r requirements.txt

RUN chmod +x deploy/run.sh deploy/cron.sh

CMD ["/app/deploy/cron.sh"]
