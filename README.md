# addr

## Requirements
* CMake
* boost
* [secp256k1](https://github.com/bitcoin-core/secp256k1)
* Rust

## Setup

1. Get all funded addresses
    1. mkdir addr_csv
    2. add *addr_csv/out?.eth.csv*
2. `$ pip3 install -r pyattacker/requirements.txt`
3. `$ bash list_addr.sh`
4. `$ make init_db`

## Usage

* cpp:
  * random: `$ make release`
  * increment: - `ENTROPY_TYPE=increment`

* py: `$ python3 bruteforce.py`
