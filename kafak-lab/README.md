# Kafka lab setup

Install Python 3, then open a terminal in the `kafak-lab` folder. Create a virtual environment to keep the lab's packages separate from your system packages.

## Windows (PowerShell)

```powershell
py -m venv .venv
.\.venv\Scripts\python.exe -m pip install --upgrade pip
.\.venv\Scripts\python.exe -m pip install confluent-kafka
```

If `py` is unavailable but `python` works, use `python -m venv .venv` for the first command. These commands use the environment directly, so activation and PowerShell execution policy changes are unnecessary.

## macOS / Linux

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install confluent-kafka
```

On Ubuntu/Debian, if creating the environment reports that `venv` is missing, run `sudo apt install python3-venv`, then retry.

## About requirements.txt

The current `requirements.txt` contains Ubuntu system packages exported by `pip freeze`, and it is missing `confluent-kafka`, which the scripts import. Use the commands above to install the required package on Windows, macOS, or Linux.

Once `requirements.txt` has been regenerated from a clean virtual environment containing the lab dependencies, users can install it with `python -m pip install -r requirements.txt`. On Windows, use `.\.venv\Scripts\python.exe` instead of `python`.

## Run the scripts

A Kafka broker must be running and reachable at `localhost:9092`. Installing `confluent-kafka` installs the Python client only.

Create the `BookLecture` topic:

```bash
python admin.py
```

Then run the producer and consumer in separate terminals:

```bash
python producer.py
```

```bash
python consumer.py
```

On macOS/Linux, activate the environment with `source .venv/bin/activate` in each terminal. On Windows, replace `python` with `.\.venv\Scripts\python.exe` in each command.

If using WSL on Windows, follow the Linux instructions and create the virtual environment inside WSL.
