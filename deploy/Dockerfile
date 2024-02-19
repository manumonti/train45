FROM python:3.12-slim

# Layer 1: Install system requirements
RUN apt-get update && apt-get install -y cron python3 python3-pip

# Set the working directory
WORKDIR /app

# Layer 2: Install python requirements
COPY requirements.txt /app
RUN pip3 install --no-cache-dir -r requirements.txt

# Layer 3: Set execution rights for the entrypoints
COPY . /app
RUN chmod +x deploy/run.sh deploy/cron.sh && \
    mkdir -p /root/.cache/log &&             \
    touch /root/.cache/log/cron.log &&       \
    chmod 644 /root/.cache/log/cron.log

# Set the defult entrypoint
CMD ["/app/deploy/cron.sh"]
