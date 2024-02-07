#!/usr/bin/python3

from urllib.parse import urljoin

import click
import requests
import rlp
from ape import project
from ape.api import AccountAPI
from ape.cli import ConnectedProviderCommand, get_user_selected_account
from ape.contracts import ContractInstance
from ape.exceptions import ContractLogicError
from ape.logging import logger
from eth_typing import HexStr
from eth_utils import to_bytes, to_int

EVENT_SIGNATURE = "0x8c5261668696ce22758910d05bab8f186d6eb247ceac2af2e82c7dc17669b036"
EXIT_ALREADY_PROCESSED_ERROR = "EXIT_ALREADY_PROCESSED"


def hex_to_bytes(data: str) -> bytes:
    return to_bytes(hexstr=HexStr(data))

def get_polygon_last_block_number(account: AccountAPI, fx_base_channel_root_tunnel: ContractInstance) -> int:

    last_blocknumber = 0
    for tx in account.history:
        if tx.method_called and tx.method_called.name == 'receiveMessage':
            last_proof_data = hex_to_bytes(tx.transaction.dict()['data'])
            last_proof = fx_base_channel_root_tunnel.decode_input(last_proof_data)[1]['inputData']
            decoded = rlp.decode(last_proof)
            blocknumber = to_int(decoded[2])
            if blocknumber > last_blocknumber:
                last_blocknumber = blocknumber

    return last_blocknumber


def get_message_sent_events(graphql_endpoint: str, last_blocknumber: int) -> [dict]:
    
    gql = """
    query AllMessagesSent {
    messageSents(where: {blockNumber_gte: """ + str(last_blocknumber) + """}, orderBy: blockNumber) {
        transactionHash
    }
    }
    """

    s = requests.session()
    s.headers = {
        'Accept': 'application/json',
        'Content-Type': 'application/json'
    }

    response = s.post(graphql_endpoint, json={'query': gql})

    data = response.json()
    messages = data['data']['messageSents']
    return messages

def push_proof(account: AccountAPI, fx_base_channel_root_tunnel: ContractInstance, proof: bytes) -> bool:
    try:
        fx_base_channel_root_tunnel.receiveMessage(proof, sender=account)
        return True
    except ContractLogicError as e:
        if e.message != EXIT_ALREADY_PROCESSED_ERROR:
            raise e
        logger.info("Transaction was processed")
        return False


def get_and_push_proof(
        account: AccountAPI, 
        fx_base_channel_root_tunnel: ContractInstance, 
        messages: [dict], 
        event_signature: str, 
        proof_generator: str
        ) -> int:
        
    processed = 0
    for event in messages:
        txhash = event['transactionHash']
        s = requests.session()
        response = s.get(urljoin(proof_generator, txhash), params={'eventSignature': event_signature})
        if response.status_code != 200:
            logger.warning("Transaction is not checkpointed")
            return processed
        
        proof = response.json()['result']
        if push_proof(account, fx_base_channel_root_tunnel, proof):
            processed += 1

    return processed


@click.command(cls=ConnectedProviderCommand)
@click.option(
    "--fx-root-tunnel",
    "-fxrt",
    help="Address of FxBaseRootTunnel contract",
    default=None,
    required=True,
    type=click.STRING,
)
@click.option(
    "--graphql-endpoint",
    "-ge",
    help="GraphQL endpoint",
    default=None,
    required=True,
    type=click.STRING,
)
@click.option(
    "--proof-generator",
    "-pg",
    help="Proof generator URI",
    default=None,
    required=True,
    type=click.STRING,
)
def cli(fx_root_tunnel, graphql_endpoint, proof_generator):

    account = get_user_selected_account()
    receiver = project.IReceiver.at(fx_root_tunnel)
    last_blocknumber = get_polygon_last_block_number(account, receiver)
    logger.debug("Last processed block number: %d", last_blocknumber)

    messages = get_message_sent_events(graphql_endpoint, last_blocknumber)
    logger.info("Got %d messages", len(messages))
    
    if len(messages) == 0:
        logger.info("No new transactions")
        return

    processed = get_and_push_proof(account, receiver, messages, EVENT_SIGNATURE, proof_generator)
    logger.info("Processed %d transactions", processed)
