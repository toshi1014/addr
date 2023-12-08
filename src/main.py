import pyattacker


def prikey2wif(prikey, testnet, compressed):
    pubkey = pyattacker.tools.prikey2pubkey(prikey)
    addr = pyattacker.tools.pubkey2addr(pubkey, testnet)
    wif = pyattacker.tools.prikey2wif(prikey, testnet, compressed)

    print(
        f"private key:\t{prikey}\npublic key:\t{pubkey}\naddr:\t{addr}\nwif:\t{wif}\n")


def wif2addr(wif, testnet):
    prikey = pyattacker.tools.wif2prikey(wif)
    pubkey = pyattacker.tools.prikey2pubkey(prikey)
    addr = pyattacker.tools.pubkey2addr(pubkey, testnet)

    print(
        f"private key:\t{prikey}\npublic key:\t{pubkey}\naddr:\t{addr}\nwif:\t{wif}\n")


def mnemonic2addr(mnemonic, network):
    if network == "btc":
        cls_hdkey = pyattacker.HDKeyBTC
    elif network == "eth":
        cls_hdkey = pyattacker.HDKeyETH
    else:
        raise ValueError("Unknown network", network)

    seed = pyattacker.bip39.mnemonics2seed(mnemonic)
    addr = cls_hdkey.seed2address(seed, witness_type="segwit")

    assert pyattacker.bip39.validate_mnemonic(mnemonic)

    print("mnemonic:", mnemonic)
    print("seed:\t", seed)
    print("addr:\t", addr, "\n")


def main():
    prikey = "E9873D79C6D87DC0FB6A5778633389F4453213303DA61F20BD67FC233AA33262"
    wif = "L1ag5Vm9SuCU4PtPebZUxsBv56SZ3RxQ8rxWHxTH9PtQfmcW3oqJ"
    mnemonic = "rail doll long permit claim wine glad layer miss thing inherit execute"
    testnet = False
    compressed = False

    # prikey2wif(prikey, testnet, compressed)
    # wif2addr(wif, testnet)

    entropy = pyattacker.bip39.gen_entropy(128)
    mnemonic = pyattacker.bip39.generate_mnemonic(entropy)
    mnemonic2addr(mnemonic, "btc")
    mnemonic2addr(mnemonic, "eth")


if __name__ == "__main__":
    main()
