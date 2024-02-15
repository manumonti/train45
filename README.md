# State Transfer Bot Polygon → Ethereum

Stateless bot monitors GraphQL endpoint for new events `MessageSent` that occurs on Polygon network. And then transfers proof to Ethereum root contract.

## Installation

We use [Ape](https://docs.apeworx.io/ape/stable/index.html) as the testing and deployment framework of this project.

### Configuring Pre-commit

To install pre-commit locally:

```bash
pre-commit install
```

## Example of usage

```bash
export WEB3_INFURA_PROJECT_ID=<Infura project ID>
export APE_ACCOUNTS_BOT_PASSPHRASE=<Passphrase for account with alias BOT>

ape run proof_bot --fx-root-tunnel 0x720754c84f0b1737801bf63c950914E0C1d4aCa2 --graphql-endpoint https://api.studio.thegraph.com/query/24143/polygonchildmumbai/version/latest --proof-generator https://proof-generator.polygon.technology/api/v1/mumbai/exit-payload/ --network :goerli:infura --account BOT
```


## Docker

##### Build

```bash
docker build -f deploy/Dockerfile -t nucypher/train45:latest .
```

##### Run

First, create the log file:

```bash
touch /var/log/cron.log
```

Then run the bot:

```bash
docker run             \
--name train45         \
--detach               \
--env-file .env        \
-f deploy/Dockerfile   \
-v /var/log/cron.log:/var/log/cron.log \
-v /var/log/:/var/log/ \
-v ~/.ape/:/root/.ape  \
nucypher/train45:latest
```

Enjoy the logs:

```bash
tail -f /var/log/cron.log
```

##### Stop

```bash
docker stop train45 && docker rm train45
```

## Docker-compose

##### Build

```bash
docker-compose build
```

##### Start (all services)

First, create the log file:

```bash
touch /var/log/cron.log
```

Then run the bot with docker-compose 
(including log server and autoupdate service):

```bash
docker-compose up -d
```

##### Stop (all services)

```bash
docker-compose down
```
