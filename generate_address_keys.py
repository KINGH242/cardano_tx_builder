import argparse
import os

from colorama import Fore
from pycardano import PaymentKeyPair, StakeKeyPair, Address, Network


def main():
    parser = argparse.ArgumentParser(description="Generate address key pairs.")

    parser.add_argument(
        "-n",
        "--name",
        help="The name of the address key pair.",
        type=str,
    )

    args = parser.parse_args()

    if args.name is None:
        parser.error(f"{Fore.MAGENTA}Name is required.{Fore.RESET}")

    payment_key_pair = PaymentKeyPair.generate()
    payment_signing_key = payment_key_pair.signing_key
    payment_verification_key = payment_key_pair.verification_key
    payment_signing_key.save(f"{args.name}.payment.skey")
    payment_verification_key.save(f"{args.name}.payment.vkey")

    stake_key_pair = StakeKeyPair.generate()
    stake_signing_key = stake_key_pair.signing_key
    stake_verification_key = stake_key_pair.verification_key
    stake_signing_key.save(f"{args.name}.stake.skey")
    stake_verification_key.save(f"{args.name}.stake.vkey")

    base_address = Address(payment_part=payment_verification_key.hash(),
                           staking_part=stake_verification_key.hash(),
                           network=Network.TESTNET)
    save_addr(str(base_address), f"{args.name}.addr")

    stake_address = Address(staking_part=payment_verification_key.hash(),
                            network=Network.TESTNET)
    save_addr(str(stake_address), f"{args.name}.stake.addr")


def save_addr(addr: str, path: str):
    """
    Save an address to a file.
    :param addr: The address to save.
    :param path: The path to save the address to.
    """
    if os.path.isfile(path) and os.stat(path).st_size > 0:
        raise IOError(f"File {path} already exists!")
    with open(path, "w") as f:
        f.write(addr)


if __name__ == "__main__":
    main()
