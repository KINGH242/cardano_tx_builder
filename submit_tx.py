import asyncio
from typing import Union

from pycardano import (
    Transaction,
    InvalidArgumentException
)
from pyogmios_client.connection import (
    create_interaction_context,
    InteractionContextOptions,
)
from pyogmios_client.enums import InteractionType
from pyogmios_client.ouroboros_mini_protocols.tx_submission.tx_submission_client import create_tx_submission_client


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