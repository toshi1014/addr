import pyattacker


def prikey2wif(prikey, testnet, compressed):
    pubkey = pyattacker.tools.prikey2pubkey(prikey)
    addr = pyattacker.tools.pubkey2addr(pubkey, testnet).decode()
    wif = pyattacker.tools.prikey2wif(prikey, testnet, compressed).decode()

    print(
        f"private key:\t{prikey}\npublic key:\t{pubkey}\naddr:\t{addr}\nwif:\t{wif}\n")


def wif2addr(wif, testnet):
    prikey = pyattacker.tools.wif2prikey(wif)
    pubkey = pyattacker.tools.prikey2pubkey(prikey)
    addr = pyattacker.tools.pubkey2addr(pubkey, testnet)

    print(
        f"private key:\t{prikey}\npublic key:\t{pubkey}\naddr:\t{addr}\nwif:\t{wif}\n")


def main():
    prikey = "E9873D79C6D87DC0FB6A5778633389F4453213303DA61F20BD67FC233AA33262"
    wif = "L1ag5Vm9SuCU4PtPebZUxsBv56SZ3RxQ8rxWHxTH9PtQfmcW3oqJ"
    testnet = False
    compressed = False


    prikey2wif(prikey, testnet, compressed)
    wif2addr(wif, testnet)

    network = "btc-legacy"

    entropy = pyattacker.bip39.gen_entropy(128)
    mnemonic = pyattacker.bip39.generate_mnemonic(entropy)

    seed = pyattacker.bip39.mnemonics2seed(mnemonic)
    addr = pyattacker.HDKey.seed2address(seed, network)

    print(f"\nentropy:\t{entropy}\nseed:\t{seed}\nmnemonic:\n\t{mnemonic}\n\naddr:\t{addr}")
    pyattacker.utils.to_clipboard(mnemonic)


if __name__ == "__main__":
    main()
