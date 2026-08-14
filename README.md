# Binary Classification Model on Hotel Cancellation Probability

Data cleaning and predictive modelling on Lisbon hotel booking records,
predicting whether a reservation will be cancelled before arrival.

I use VS Code with the Python (`ms-python.python`), Python Environments
(`ms-python.vscode-python-envs`), and Jupyter (`ms-toolsai.jupyter`)
extensions. The Python Environments extension activates `.venv`
in the integrated terminal on its own, so there is nothing to source.

## Setup

Clone into your empty working directory:

    git clone https://codeberg.org/daraknet/Lisbon.git .

Python is pinned to **3.12.14** in `.python-version` and `mise.toml`.

### With mise (what I use)

    mise trust
    mise install      # installs Python 3.12.14
    mise run install  # creates and activates .venv & installs dependencies

If `mise run install` fails, install the dependencies directly:

    python -m pip install --no-cache-dir -U -r requirements.txt --prefer-binary

### With uv (recommended)

uv is becoming the standard for Python project management. It installs
the interpreter, creates the venv, and installs packages in one step.
See https://docs.astral.sh/uv/

    uv sync

### Without either

Install Python 3.12.14 however you prefer — pyenv, asdf, or python.org.

    python3 -m venv .venv
    python -m pip install -r requirements.txt

## VS Code

Open the folder and select `./.venv/bin/python` as the interpreter
(Command Palette → *Python: Select Interpreter*). It normally prompts
on its own.

Outside VS Code, activate manually: `source .venv/bin/activate`
(`.venv\Scripts\Activate.ps1` on Windows).

## Dependencies

`requirements.txt` and `pyproject.toml` cover the bootstrap only —
enough to open and run the notebook. Additional libraries are installed
from within `lisbon.ipynb` as the analysis proceeds.