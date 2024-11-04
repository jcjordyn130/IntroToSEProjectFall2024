# backend-dev
This is the backend code for Sprint 3.

## Installing
Before runiing the backend, the dependencies need to be installed.

This can be done using `pip` and the `requirements.txt` file as so:

`pip3 install --user -r requirements.txt`

## Running
To run a local testing instance, use the `main.py` script.

It will run an instance of the backend bound to `127.0.0.1:5000`, with debugging enabled.

To connect to the daemon from other machines, edit the script and change `127.0.0.1` to `0.0.0.0`.

## Structure
- api: The Flask based web API 
- database: The custom database interface class based off of SQLite3
- client.py: A testing client for the web API
- gendummydb.py: Creates a fake database for testing, one is already in the repository as `db.sqlite3`.
- main.py: Simple script to run flask with the appropriate arguments, `flask run` does the same thing.
