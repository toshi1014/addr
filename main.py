import src


def prikey2wif(prikey, testnet, compressed):
    pubkey = src.tools.prikey2pubkey(prikey)
    addr = src.tools.pubkey2addr(pubkey, testnet)
    wif = src.tools.prikey2wif(prikey, testnet, compressed)

    print(
        f"private key:\t{prikey}\npublic key:\t{pubkey}\naddr:\t{addr}\nwif:\t{wif}\n")


def wif2addr(wif, testnet):
    prikey = src.tools.wif2prikey(wif)
    pubkey = src.tools.prikey2pubkey(prikey)
    addr = src.tools.pubkey2addr(pubkey, testnet)

    print(
        f"private key:\t{prikey}\npublic key:\t{pubkey}\naddr:\t{addr}\nwif:\t{wif}\n")


def mnemonic2addr(mnemonic):
    seed = src.bip39.mnemonics2seed(mnemonic)
    hdkey = src.HDKey.from_seed(seed)
    addr = src.HDKey.get_address(hdkey)

    assert src.bip39.validate_mnemonic(mnemonic)

    print("mnemonic:\t", mnemonic)
    print("seed:\t", seed)
    print("addr:\t", addr)


def main():
    prikey = "E9873D79C6D87DC0FB6A5778633389F4453213303DA61F20BD67FC233AA33262"
    wif = "L1ag5Vm9SuCU4PtPebZUxsBv56SZ3RxQ8rxWHxTH9PtQfmcW3oqJ"
    # wif = "5HueCGU8rMjxEXxiPuD5BDku4MkFqeZyd4dZ1jvhTVqvbTLvyTJ"
    mnemonic = "rail doll long permit claim wine glad layer miss thing inherit execute"
    testnet = False
    compressed = False

    # prikey2wif(prikey, testnet, compressed)
    mnemonic2addr(mnemonic)
    # wif2addr(wif, testnet)



if __name__ == "__main__":
    main()
