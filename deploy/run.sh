#!/bin/bash

echo "Running proof bot"

cd /app

ape run proof_bot           \
--network $NETWORK          \
--account $ACCOUNT          \
--fx-root-tunnel $TUNNEL    \
--graphql-endpoint $GQL_URL \
--proof-generator $PROOFS_URL
