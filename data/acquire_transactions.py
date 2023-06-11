"""Script to pull on-chain transaction data and output JSON for post-processing"""
from __future__ import annotations

import json
import os
import time
from json import JSONEncoder
from typing import Iterable, Sequence

import requests
import toml
from eth_utils.address import to_checksum_address
from hexbytes import HexBytes
from numpy import isin
from web3 import Web3
from web3.contract.contract import Contract, ContractEvent
from web3.datastructures import AttributeDict, MutableAttributeDict
from web3.middleware import geth_poa
from web3.types import ABIEvent, BlockData, EventData, LogReceipt, TxData, TxReceipt

# python `open` will infer the encoding if we do not specified, which is the behavior we want for now
# pylint: disable=unspecified-encoding

# pylint: disable=too-many-locals


class ExtendedJSONEncoder(JSONEncoder):
    """Overrides json encoder to handle hex inputs"""

    def default(self, o):
        if isinstance(o, HexBytes):
            return o.hex()
        if isinstance(o, (AttributeDict, MutableAttributeDict)):
            return dict(o)
        return super().default(o)


def save_config(config, file_path):
    """Saves the config file in TOML format"""
    with open(file_path, "w", encoding="UTF-8") as file:
        toml.dump(config, file)


def load_abi(file_path):
    """Load the Application Binary Interface (ABI) from a JSON file"""
    with open(file_path, "r") as file:
        data = json.load(file)
    return data["abi"]


def recursive_dict_conversion(obj):
    """Recursively converts a dictionary to convert objects to hex values"""
    if isinstance(obj, HexBytes):
        return obj.hex()
    if isinstance(obj, dict):
        return {key: recursive_dict_conversion(value) for key, value in obj.items()}
    if hasattr(obj, "items"):
        return {key: recursive_dict_conversion(value) for key, value in obj.items()}
    return obj


def get_event_object(
    web3_container: Web3, contract: Contract, log: LogReceipt, tx_receipt: TxReceipt
) -> tuple[EventData, ABIEvent] | tuple[None, None]:
    """Retrieves the event object and anonymous types for a  given contract and log"""
    abi_events = [abi for abi in contract.abi if abi["type"] == "event"]  # type: ignore
    for event in abi_events:  # type: ignore
        # Get event signature components
        name = event["name"]  # type: ignore
        inputs = [param["type"] for param in event["inputs"]]  # type: ignore
        inputs = ",".join(inputs)
        # Hash event signature
        event_signature_text = f"{name}({inputs})"
        event_signature_hex = web3_container.keccak(text=event_signature_text).hex()
        # Find match between log's event signature and ABI's event signature
        receipt_event_signature_hex = log["topics"][0].hex()
        if event_signature_hex == receipt_event_signature_hex:
            # Decode matching log
            contract_event: ContractEvent = contract.events[event["name"]]()  # type: ignore
            event_data: EventData = contract_event.process_receipt(tx_receipt)[0]
            return event_data, event  # type: ignore
    return (None, None)


def fetch_and_decode_logs(web3_container: Web3, contract: Contract, tx_receipt: TxReceipt):
    """Decode logs from a transaction receipt"""
    logs = []
    if tx_receipt.get("logs"):
        for log in tx_receipt["logs"]:
            event_data, event = get_event_object(web3_container, contract, log, tx_receipt)
            if event_data and event:
                # TODO: For some reason it thinks `log` is `str` instead of `EventData`
                formatted_log = dict(event_data)
                formatted_log["event"] = event.get("name")
                formatted_log["args"] = dict(event_data["args"])
                logs.append(formatted_log)
    return logs


def fetch_transactions(web3_container: Web3, contract: Contract, start_block: int, ending_block: int):
    """Fetch transactions related to the hyperdrive_address contract"""
    decoded_transactions = []
    for block_number in range(start_block, ending_block):
        block: BlockData = web3_container.eth.get_block(block_number, full_transactions=True)
        print(f"{block.get('number')=}")

        transactions = block.get("transactions")
        if not transactions:
            print(f"no transactions in block {block.get('number')}")
            continue

        for transaction in transactions:
            if isinstance(transaction, HexBytes):
                print("transaction HexBytes")
                continue
            if transaction.get("to") != contract.address:
                print("transaction not from hyperdrive contract")
                continue
            transaction_dict = dict(transaction)
            # Convert the HexBytes fields to their hex representation
            tx_hash = transaction.get("hash") or HexBytes("")
            transaction_dict["hash"] = tx_hash.hex()
            # Decode the transaction input
            try:
                method, params = contract.decode_function_input(transaction["input"])
                transaction_dict["input"] = {"method": method.fn_name, "params": params}
            except ValueError:  # if the input is not meant for the contract, ignore it
                continue
            tx_receipt = web3_container.eth.get_transaction_receipt(tx_hash)
            logs = fetch_and_decode_logs(web3_container, contract, tx_receipt)
            decoded_transactions.append(
                {"transaction": transaction_dict, "logs": logs, "receipt": recursive_dict_conversion(tx_receipt)}
            )
    return decoded_transactions


def main(config_file_path, contracts_url, ethereum_node, save_dir, abi_file_path):
    """Main execution entry point"""
    # Define necessary variables/objects
    if not os.path.exists(save_dir):  # create save_dir if necessary
        os.makedirs(save_dir)
    transactions_output_file = os.path.join(save_dir, "transactions.json")
    # Load the ABI from the JSON file
    with open(abi_file_path, "r") as file:
        abi = json.load(file)["abi"]
    # Connect to the Ethereum node
    web3_container = Web3(Web3.HTTPProvider(ethereum_node))
    web3_container.middleware_onion.inject(geth_poa.geth_poa_middleware, layer=0)
    # Main loop to fetch transactions continuously
    while True:
        # Send a request to the local server to fetch the deployed contract addresses
        response = requests.get(contracts_url, timeout=60)
        # Check the status code and retry the request if it fails
        if response.status_code != 200:
            print(f"Request failed with status code {response.status_code} @ {time.ctime()}")
            time.sleep(10)
            continue
        # Load the deployed contract addresses from the server response
        depl_addrs = response.json()
        hyperdrive_address = depl_addrs["hyperdrive"]
        contract = web3_container.eth.contract(address=to_checksum_address(hyperdrive_address), abi=abi)
        # Load the starting block number from the config file
        with open(config_file_path, "r") as file:
            config = toml.load(file)
            starting_block = config["settings"]["startBlock"]
        # Get the current block number from the Ethereum node
        current_block = web3_container.eth.block_number
        # Fetch transactions related to the hyperdrive_address contract
        ending_block = min(starting_block + 10, current_block)
        transactions = fetch_transactions(web3_container, contract, starting_block, ending_block)
        # Save the updated transactions to the output file with custom encoder
        with open(transactions_output_file, "w", encoding="UTF-8") as file:
            json.dump(transactions, file, indent=2, cls=ExtendedJSONEncoder)
        # Update the starting block number in the config file
        config["settings"]["startBlock"] = ending_block
        # Save the updated config data to the TOML file
        # save_config(config, config_file_path)
        # Wait for 10 seconds before fetching transactions again
        if ending_block == current_block:
            time.sleep(10)


if __name__ == "__main__":
    CONFIG_FILE_PATH = "./data/config/dataConfig.toml"
    CONTRACTS_URL = "http://localhost:80/addresses.json"
    ETHEREUM_NODE = "http://localhost:8545"
    SAVE_DIR = ".logging"
    ABI_FILE_PATH = "./hyperdrive_solidity/.build/Hyperdrive.json"
    main(CONFIG_FILE_PATH, CONTRACTS_URL, ETHEREUM_NODE, SAVE_DIR, ABI_FILE_PATH)
