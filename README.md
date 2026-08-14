# Binary Classification Model on Hotel Cancellation Probability

Data cleaning and predictive modelling on Lisbon hotel booking records,
predicting **at booking time** whether a reservation will be cancelled
before arrival.

## Repository layout

| Path | What it is |
|------|------------|
| `lisbon.ipynb` | The full analysis: EDA, cleaning, feature engineering, model training, tuning and evaluation. Ends by writing the serialised model to `artifacts/`. Rendered to HTML, this is the report. |
| `score_booking.py` | Production scoring script: ingests one new booking as JSON, outputs cancellation probability + decision. |
| `booking.json` | Sample input so the scorer can be run immediately. |
| `artifacts/` | Written by the notebook: fitted pipeline (`model.joblib`), `metadata.json`, and the guest/history lookup tables the scorer uses. |
| `data/` | The five raw CSV files (`H1.csv`, `H2.csv`, `Guests.csv`, `Payments.csv`, `Weather.csv`). Never modified; the notebook only reads them. |
| `requirements.txt` | Pinned dependencies. |

## Setup

I use VS Code with the Python (`ms-python.python`), Python Environments
(`ms-python.vscode-python-envs`), and Jupyter (`ms-toolsai.jupyter`)
extensions. The Python Environments extension activates `.venv`
in the integrated terminal on its own, so there is nothing to source.

Clone into your empty working directory:

    git clone OR download the .ZIP, extract its contents here.

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

## Running everything

After the environment setup below, with the five CSVs in `data/`:

1. **Training / report**: run `lisbon.ipynb` top to bottom (VS Code "Run All", or
   headless: `jupyter execute --inplace lisbon.ipynb`). Takes a few minutes; all
   randomness is seeded (`RANDOM_STATE = 42`), so results reproduce exactly.
2. **Render the report**: `jupyter nbconvert --to html lisbon.ipynb`
   (produces `lisbon.html`).
3. **Score an example booking**:
   `python score_booking.py booking.json`

## Use of AI tools (declaration)

Claude Code (Anthropic) was used as a coding assistant throughout: exploring the
data, drafting notebook cells, charts and the scoring script, under my direction
and review. All modelling decisions, justifications and conclusions were reviewed
and are my own responsibility.