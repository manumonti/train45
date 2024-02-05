#!/usr/bin/python3

import requests
from ape import project
import rlp
from eth_typing import HexStr
from eth_utils import to_bytes, to_int
from ape.api import AccountAPI
from ape.contracts import ContractInstance
from ape.cli import get_user_selected_account
from ape.exceptions import ContractLogicError


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

def push_proof(account: AccountAPI, fx_base_channel_root_tunnel: ContractInstance, proof: bytes):
    try:
        fx_base_channel_root_tunnel.receiveMessage(proof, sender=account)
    except ContractLogicError as e:
        if e.message != "EXIT_ALREADY_PROCESSED":
            raise e
        print("processed")


def get_and_push_proof(
        account: AccountAPI, 
        fx_base_channel_root_tunnel: ContractInstance, 
        messages: [dict], 
        event_signature: str, 
        proof_generator: str
        ):
        
    for event in messages:
        txhash = event['transactionHash']
        s = requests.session()
        response = s.get(proof_generator + txhash, params={'eventSignature': event_signature})
        if response.status_code != 200:
            assert False, "No proof"
        proof = response.json()['result']
        push_proof(account, fx_base_channel_root_tunnel, proof)


def main():  

    account = get_user_selected_account()
    polygon_root_address = "0x720754c84f0b1737801bf63c950914E0C1d4aCa2"

    graphql_endpoint = "https://api.studio.thegraph.com/query/24143/polygonchildmumbai/version/latest"

    event_signature = '0x8c5261668696ce22758910d05bab8f186d6eb247ceac2af2e82c7dc17669b036'
    proof_generator = "https://proof-generator.polygon.technology/api/v1/mumbai/exit-payload/"

    receiver = project.IReceiver.at(polygon_root_address)
    last_blocknumber = get_polygon_last_block_number(account, receiver)
    messages = get_message_sent_events(graphql_endpoint, last_blocknumber)
    
    print(messages)
    if len(messages) == 0:
        print("Nothing to push")
        return

    get_and_push_proof(account, receiver, messages, event_signature, proof_generator)