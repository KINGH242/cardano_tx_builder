import argparse
import asyncio
import os

from blockfrost import ApiUrls
from colorama import Fore
from pycardano import (
    Address,
    BlockFrostChainContext,
    Network,
    PaymentSigningKey,
    PaymentVerificationKey,
    TransactionBuilder,
    TransactionOutput,
    StakeVerificationKey
)

from submit_tx import send_tx

BLOCKFROST_API_KEY = os.environ["BLOCKFROST_API_KEY"]


async def main():
    """
    Send ADA from one address to another.
    """
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
    await send_tx(tx)
    print("DONE")

    print(
        f"Tracking: {Fore.GREEN}https://preprod.cardanoscan.io/transaction/{tx.id}{Fore.RESET}\n"
    )


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
