## Cardano Transaction Builder

This project contains a simple command line tool to build Cardano transactions.
It also contains a CLI script to generate payment and stake keys, addresses, and transactions.

It uses the PyCardano serialization library to build transactions, and the Opshin library for Plutus script.

It also uses PyOgmios for transaction submission.

## Installation

This project uses [Poetry](https://python-poetry.org/) in development to create a virtual environment and manage
dependencies.
To install poetry, run

```shell
curl -sSL https://raw.githubusercontent.com/python-poetry/poetry/master/get-poetry.py | python -
```

Then, from the same directory as `pyproject.toml`, run

```shell
poetry install
```

Run `poetry` commands from this same directory to manage your development environment and/or setup the virtual
environment created in the last step in your IDE.

See [Poetry Docs](https://python-poetry.org/docs/cli/) for more info.

## Examples

```shell
poetry run python main.py -h
```

```shell 
poetry run python main.py -s full_test -a 1000000 -r addr_testtherestoftheaddresswouldbehere1
```


## Gift Contract Example

The file `gift.py` contains an example gift contract written using Opshin. Run the following from within to build the contract:

```shell
poetry run opshin build gift.py
```

The file `generate_address_keys.py` contains an example of how to generate payment and stake keys and addresses. It can
be used to generate the keys and addresses needed to run the gift contract example.

```shell
poetry run python generate_address_keys.py -n giver
poetry run python generate_address_keys.py -n taker
```

The file `submit_tx.py` contains the code to submit a transaction using PyOgmios.

The `demo_gift_contract.py` file is used to demo the gift contract by locking funds from the giver address and then
claiming them from the taker address. The giver and taker addresses are hardcoded in the file, so you will need to
update them to the addresses generated in the previous step. To run the demo, run the following:

```shell
poetry run python demo_gift_contract.py
```

