import os
import random
from bitcoinlib.wallets import Wallet, wallet_delete_if_exists
from tqdm import tqdm
import bip39
import db_handlers
from hdkey_btc import HDKeyBTC
from hdkey_eth import HDKeyETH
import utils


config = utils.read_config()


def init_wallet_obj(mnemonic, witness_type, wallet_name="Wallet1"):
    if wallet_delete_if_exists(wallet_name):
        ...

    return Wallet.create(
        name=wallet_name,
        keys=mnemonic,
        network="bitcoin",
        witness_type=witness_type,
    )


def has_balance_all(mnemonic, db, is_all=False):
    seed = bip39.mnemonics2seed(mnemonic)

    addr_legacy = HDKeyBTC.seed2address(
        seed=seed, witness_type="legacy", network="btc"
    )
    addr_segwit = HDKeyBTC.seed2address(
        seed=seed, witness_type="segwit", network="btc"
    )
    addr_eth = HDKeyETH.seed2address(seed=seed)

    if is_all:
        return db.find(addr_legacy) & db.find(addr_segwit) & db.find(addr_eth)
    else:
        return db.find(addr_legacy) or db.find(addr_segwit) or db.find(addr_eth)


def has_balance_eth(mnemonic, db, is_all=False):
    seed = bip39.mnemonics2seed(mnemonic)
    addr_eth = HDKeyETH.seed2address(seed=seed)
    return db.find(addr_eth)


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


def ping(func_has_balance, db):
    mnemonic = bip39.generate_mnemonic(
        config["PING_DATA"]["entropy"]
    )
    assert func_has_balance(mnemonic, db, is_all=True)


def found(mnemonic):
    utils.notify(mnemonic)
    with open("found.txt", mode="a", encoding="utf-8") as f:
        f.write(mnemonic + "\n")


@utils.with_timer(template="Delta: {time} (s)")
def run(strength, db):
    assert strength in bip39.SUPPORTED_STRENGTH

    # func_has_balance = has_balance_all
    func_has_balance = has_balance_eth

    # chunk_bits = 6
    # lim = 2**(11 * (12 - chunk_bits))
    # rng = range(lim)
    lim = 2 ** strength
    rng = gen(lim)

    for i in tqdm(rng, total=lim/2**100):   # small total for show
        entropy = tmp_gen_entropy(i, strength, lim)
        mnemonic = bip39.generate_mnemonic(entropy)

        if func_has_balance(mnemonic, db):
            print(f"{i}: {mnemonic}")
            found(mnemonic)

        if i % 100000 == 0:
            ping(func_has_balance, db)
            print("ping", i)


def main():
    if config["DB_TYPE"] == "sqlite":
        db = db_handlers.DBSqlite()
    elif config["DB_TYPE"] == "postgres":
        db = db_handlers.DBPostgres()
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
