import asyncio
import os
from typing import Tuple

from blockfrost import ApiUrls
from pycardano import (
    Address,
    PaymentVerificationKey,
    PaymentSigningKey,
    plutus_script_hash,
    TransactionBuilder,
    TransactionOutput,
    PlutusData,
    Redeemer,
    PlutusV2Script,
    Network,
    datum_hash,
)
from pycardano import BlockFrostChainContext

from gift import CancelDatum
from submit_tx import send_tx

BLOCKFROST_API_KEY = os.environ["BLOCKFROST_API_KEY"]
NETWORK = Network.TESTNET
context = BlockFrostChainContext(BLOCKFROST_API_KEY, base_url=ApiUrls.preprod.value)


def create_script_address() -> Tuple[Address, PlutusV2Script]:
    """
    Create a script address and save the script to a file.
    :return: The script address and the script.
    """
    with open("build/gift/script.cbor", "r") as f:
        script_hex = f.read()
    script = PlutusV2Script(bytes.fromhex(script_hex))

    script_hash = plutus_script_hash(script)
    address = Address(script_hash, network=NETWORK)

    print(f"Gift script address: {address}")
    return address


async def send_funds_to_script_address(address: Address):
    """
    Send funds to the script address.
    :param address: The script address.
    """
    giver_payment_vkey = PaymentVerificationKey.load("giver.payment.vkey")
    giver_payment_skey = PaymentSigningKey.load("giver.payment.skey")
    giver_address = Address(giver_payment_vkey.hash(), network=NETWORK)

    taker_payment_vkey = PaymentVerificationKey.load("taker.payment.vkey")

    builder = TransactionBuilder(context)
    builder.add_input_address(giver_address)

    datum = CancelDatum(taker_payment_vkey.hash().to_primitive())
    builder.add_output(
        TransactionOutput(address, 50_000_000, datum_hash=datum_hash(datum))
    )
    signed_tx = builder.build_and_sign([giver_payment_skey], giver_address)
    print(f"Signed transaction: {signed_tx.to_cbor_hex()}")

    # context.submit_tx(signed_tx.to_cbor_hex())

    # online submit
    print("Submitting the transaction via PyOgmios...")
    await send_tx(signed_tx)
    print("DONE")


async def take_funds_from_script(address: Address, script: PlutusV2Script):
    """
    Take funds from the script address.
    :param address: The script address.
    :param script: The script.
    """
    redeemer = Redeemer(PlutusData())  # The plutus equivalent of None

    utxo_to_spend = context.utxos(str(address))[0]

    taker_payment_vkey = PaymentVerificationKey.load("taker.payment.vkey")
    taker_payment_skey = PaymentSigningKey.load("taker.payment.skey")
    taker_address = Address(taker_payment_vkey.hash(), network=NETWORK)
    datum = CancelDatum(taker_payment_vkey.hash().to_primitive())

    builder = TransactionBuilder(context)
    builder.add_script_input(utxo_to_spend, script, datum, redeemer)
    take_output = TransactionOutput(taker_address, 25123456)
    builder.add_output(take_output)

    non_nft_utxo = None
    for utxo in context.utxos(str(taker_address)):
        # multi_asset should be empty for collateral utxo
        if not utxo.output.amount.multi_asset:
            non_nft_utxo = utxo
            break

    builder.collaterals.append(non_nft_utxo)
    builder.required_signers = [taker_payment_skey.hash()]

    signed_tx = builder.build_and_sign([taker_payment_skey], taker_address)

    # context.submit_tx(signed_tx.to_cbor_hex())

    # online submit
    print("Submitting the transaction via PyOgmios...")
    await send_tx(signed_tx)
    print("DONE")


async def main():
    """
    Send funds to the script address, then take funds from the script address.
    """
    script_address, gift_script = create_script_address()

    await send_funds_to_script_address(script_address)

    await take_funds_from_script(script_address, gift_script)


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
