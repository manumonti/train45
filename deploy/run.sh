#!/bin/bash

cd /app
echo "The train is leaving the station"
ape run proof_bot \
--network $NETWORK          \
--account $ACCOUNT          \
--fx-root-tunnel $TUNNEL    \
--graphql-endpoint $GQL_URL \
--proof-generator $PROOFS_URL
