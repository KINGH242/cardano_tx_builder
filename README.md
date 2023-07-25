
## Cardano Transaction Builder

This project uses [Poetry](https://python-poetry.org/) in development to create a virtual environment and manage dependencies.
To install poetry, run

```shell
curl -sSL https://raw.githubusercontent.com/python-poetry/poetry/master/get-poetry.py | python -
```

Then, from the same directory as `pyproject.toml`, run

```shell
poetry install
```

Run `poetry` commands from this same directory to manage your development environment and/or setup the virtual environment created in the last step in your IDE.


See [Poetry Docs](https://python-poetry.org/docs/cli/) for more info.

## Examples

```shell
poetry run python main.py -h
```

```shell 
poetry run python main.py -s full_test -a 1000000 -r addr_testtherestoftheaddresswouldbehere1
```
