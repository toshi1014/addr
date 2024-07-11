# addr

## Requirements
* CMake
* boost
* [secp256k1](https://github.com/bitcoin-core/secp256k1)
* Rust

## Setup
1. `$ bash setup.sh`
2. `$ pip3 install -r pyattacker/requirements.txt`
3. prepare db

### DB
1. Get all funded addresses (*addr_csv/out?.eth.csv*)
4. `$ bash list_addr.sh`
5. `$ make init_db`


## Usage

* cpp:
  * random: `$ make release`
  * increment: `$ make release ENTROPY_TYPE=increment`

* py: `$ python3 bruteforce.py`


### Docker

* build: `$ docker build -t img-addr . --no-cache --rm`

* run
  * `$ docker run --rm img-addr`

* run -it
  1. `$ docker run -it --rm --name cont-addr img-addr bash`
  2. make release
