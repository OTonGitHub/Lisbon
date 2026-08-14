How to run this project anywhere.
I use VSCode with the Jupyter extension (ms-toolsai.jupyter) &
the Python extension (ms-python.python).

Open the terminal in your working directory.
Clone this repo into your working directory using `git clone https://codeberg.org/daraknet/Lisbon.git .`

Python version is pinned in `.python-version` (3.12.14 for this project).
Most tool managers recognize this idiomatic version file.

I use mise.jdx to manage binaries. Note that recent mise versions
don't read `.python-version` unless you opt in once:

    mise settings add idiomatic_version_file_enable_tools python
    mise install

Or install 3.12.14 however you prefer — pyenv, asdf, or python.org.

Then create and activate the virtual environment:

    python3 -m venv .venv
    source .venv/bin/activate

VS Code should prompt to use this environment for the workspace — accept it.

Install dependencies:

    python -m pip install -r requirements.txt

Alternatively, if you use uv (https://docs.astral.sh/uv/), `uv sync`
handles the interpreter, venv, and packages in one step using the
included pyproject.toml.

Python binary is version controlling using a .python-version file.
Most tool management systems recognize idiomatic version files such as this.

I use mise.jdx for managing all my binaries so I will simply run `mise install`
OR, you can simply install the version pinned in the `.python-version` file (3.12.14 for this Project).

I recommend using uv (from https://docs.astral.sh/uv/) to manage python binaries and packages, it syncs
everythign including the kernel for VSCode to use. But I don't need a fancy tool. It's up to you how you want to set it up, but I will include a "pyproject.toml" file if you want to use UV.

Point is, use this binary to activate the virtual envronment using the correct binary,
VSCode will automatically

Now make sure your shell is using the correct python version by running `python --version`

Then run, `python -m venv .venv` to create your virtual environment for this Project using the correct Python version.

The Python VSCode should automatically detect this environment prompt to use this envrionment for the workspace press yes.

Now before getting started, Install all the requirements using the following command

> `python -m pip install --no-cache-dir -U -r requirements.txt --prefer-binary`
