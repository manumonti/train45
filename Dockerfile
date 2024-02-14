FROM python:3.12-slim

RUN apt-get update && apt-get install -y cron python3 python3-pip

WORKDIR /app

COPY . /app

RUN pip3 install --no-cache-dir -r requirements.txt
RUN chmod +x run.sh
RUN chmod +x cron.sh

CMD ["cron.sh"]
