from src.tools import prikey2pubkey, pubkey2addr, prikey2wif, wif2prikey


def all(prikey, testnet, compressed):
    pubkey = prikey2pubkey(prikey)
    addr = pubkey2addr(pubkey, testnet)
    wif = prikey2wif(prikey, testnet, compressed)

    print(
        f"private key:\t{prikey}\npublic key:\t{pubkey}\naddr:\t{addr}\nwif:\t{wif}\n")


def wif2addr(wif, testnet):
    prikey = wif2prikey(wif)
    pubkey = prikey2pubkey(prikey)
    addr = pubkey2addr(pubkey, testnet)

    print(
        f"private key:\t{prikey}\npublic key:\t{pubkey}\naddr:\t{addr}\nwif:\t{wif}\n")


def main():
    prikey = "E9873D79C6D87DC0FB6A5778633389F4453213303DA61F20BD67FC233AA33262"
    wif = "L1ag5Vm9SuCU4PtPebZUxsBv56SZ3RxQ8rxWHxTH9PtQfmcW3oqJ"
    # wif = "5HueCGU8rMjxEXxiPuD5BDku4MkFqeZyd4dZ1jvhTVqvbTLvyTJ"

    testnet = False
    compressed = False

    # public_key = "02e8408fa3d2f9270e9bc8bb6af924ab7152f7ba9234d1159f2b79a09a6ef91720"
    # test()
    all(prikey, testnet, compressed)
    # wif2addr(wif, testnet)
    # print(is_valid_wif(wif))


if __name__ == "__main__":
    main()
