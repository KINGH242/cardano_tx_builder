import argparse
import asyncio
import os
from typing import Union

from blockfrost import ApiUrls
from colorama import Fore
from pycardano import (
    Address,
    BlockFrostChainContext,
    Network,
    PaymentSigningKey,
    PaymentVerificationKey,
    Transaction,
    TransactionBuilder,
    TransactionOutput,
    StakeVerificationKey
)
from pyogmios_client.connection import (
    create_interaction_context,
    InteractionContextOptions,
)
from pyogmios_client.enums import InteractionType
from pyogmios_client.ouroboros_mini_protocols.tx_submission.tx_submission_client import create_tx_submission_client


async def main():
    BLOCKFROST_API_KEY = os.environ["BLOCKFROST_API_KEY"]

    parser = argparse.ArgumentParser(description="Script to send ADA from one address to another.")

    parser.add_argument(
        "-a",
        "--amount-to-send",
        help="The amount of ADA to send in lovelace.",
        type=int,
    )

    parser.add_argument(
        "-s",
        "--sender-address",
        help="The sender payment address name. If used, the script will check the current working "
             "directory for from-address-name.key_body and from-address-name.addr files.",
        type=str,
    )

    parser.add_argument(
        "-r",
        "--receiver-address",
        help="The receiver payment address name. If used, the script will check the current working "
             "directory for from-address-name.key_body and from-address-name.addr files.",
        type=str,
    )

    args = parser.parse_args()

    # Use testnet
    network = Network.TESTNET
    context = BlockFrostChainContext(BLOCKFROST_API_KEY, base_url=ApiUrls.preprod.value)

    if args.sender_address is None or args.receiver_address is None:
        parser.error(f"{Fore.MAGENTA}Sender address and Receiver address is required.{Fore.RESET}")

    payment_signing_key = PaymentSigningKey.load(f"{args.sender_address}.payment.skey")
    payment_verification_key = PaymentVerificationKey.load(f"{args.sender_address}.payment.vkey")
    stake_verification_key = StakeVerificationKey.load(f"{args.sender_address}.stake.vkey")

    sender_address = Address(payment_verification_key.hash(), stake_verification_key.hash(), network)
    receiver_address = args.receiver_address

    print(f"Sender Address: {Fore.GREEN}{sender_address}{Fore.RESET}")
    print(f"Receiver Address: {Fore.GREEN}{receiver_address}{Fore.RESET}")
    print(f"Deposit: {Fore.GREEN}{args.amount_to_send}{Fore.RESET}")

    # Using TransactionBuilder
    builder = TransactionBuilder(context)
    builder.add_input_address(sender_address)
    # Get all UTxOs currently sitting at this address
    utxos = context.utxos(sender_address)
    print(f"UTXOs: {Fore.GREEN}{utxos}{Fore.RESET}")
    builder.add_output(TransactionOutput.from_primitive([receiver_address, args.amount_to_send]))
    builder.ttl = 3600
    tx = builder.build_and_sign([payment_signing_key], change_address=sender_address)

    # Show the TxID
    print(f"TxID is: {Fore.GREEN}{tx.id}{Fore.RESET}")

    # online submit
    print("Submitting the transaction via PyOgmios...")
    # send_tx(tx)
    print("DONE")

    print(
        f"Tracking: {Fore.GREEN}https://preprod.cardanoscan.io/transaction/{tx.id}{Fore.RESET}\n"
    )


async def send_tx(tx: Union[Transaction, bytes, str]):
    """
    This run the tx submission client and print the output.
    """
    if isinstance(tx, Transaction):
        tx_cbor = tx.to_cbor()
    elif isinstance(tx, bytes):
        tx_cbor = tx
    else:
        raise InvalidArgumentException(
            f"Invalid transaction type: {type(tx)}, expected Transaction, bytes, or str"
        )
    interaction_context_options = InteractionContextOptions(
        interaction_type=InteractionType.ONE_TIME, log_level="INFO"
    )
    interaction_context = await create_interaction_context(
        options=interaction_context_options
    )
    await asyncio.sleep(1)
    print(interaction_context.socket.sock.connected)

    tx_submission_client = await create_tx_submission_client(
        interaction_context
    )

    print("Submit Tx")
    result = await tx_submission_client.submit_tx(tx_cbor)
    print(f"Transaction submission result: {result}")


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
