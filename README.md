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

To build docker image:

```bash
docker build -t nucypher/train45:latest .
```

Setup up one log file:

```
touch /var/log/cron.log
```

Run the container:

```bash
docker run             \
--detach               \
--restart always       \
--name train45         \
--env-file .env        \
-v /var/log/cron.log:/var/log/cron.log \
-v /var/log/:/var/log/ \
-v ~/.ape/:/root/.ape  \
nucypher/train45:latest
```

## Logging Server 

Mount the log file to an alpine container (this only uses ~300kb of memory):

```bash
docker run       \
--name logserver \
--detach         \
--restart always \
-v /var/log/cron.log:/var/log/cron.log \
alpine tail -f /var/log/cron.log

```

Launch the log server:

```bash
docker run       \
--name dozzle    \
--detach         \
--restart always \
--volume=/var/run/docker.sock:/var/run/docker.sock \
-p 8080:8080     \
amir20/dozzle
```

## Automatic Updates

```bash
docker run 
--name watchtower \
--detach          \
--restart always  \
--volume /var/run/docker.sock:/var/run/docker.sock \
containrrr/watchtower train45
```
