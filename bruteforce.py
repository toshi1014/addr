import os
import random
from bitcoinlib.wallets import Wallet, wallet_delete_if_exists
from tqdm import tqdm
import src
import init_db


def init_wallet_obj(mnemonic, witness_type, wallet_name="Wallet1"):
    if wallet_delete_if_exists(wallet_name):
        ...

    return Wallet.create(
        name=wallet_name,
        keys=mnemonic,
        network="bitcoin",
        witness_type=witness_type,
    )


def has_balance_network(mnemonic, _):
    b1 = init_wallet_obj(mnemonic, "legacy").balance()
    b2 = init_wallet_obj(mnemonic, "segwit").balance()
    return (b1 + b2) > 0


def has_balance_local(mnemonic, db):
    seed = src.bip39.mnemonics2seed(mnemonic)
    hdkey = src.HDKey.from_seed(seed)
    addr_legacy = src.HDKey.get_address(hdkey=hdkey, witness_type="legacy")
    addr_segwit = src.HDKey.get_address(hdkey=hdkey, witness_type="segwit")

    return db.find(addr_legacy) or db.find(addr_segwit)


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
    mnemonic = src.bip39.generate_mnemonic(
        init_db.PING_DATA["entropy"]
    )
    assert func_has_balance(mnemonic, db)


def found(mnemonic):
    src.utils.notify(mnemonic)
    with open("found.txt", mode="a", encoding="utf-8") as f:
        f.write(mnemonic + "\n")


@src.utils.with_timer(template="Delta: {time} (s)")
def run(strength, db):
    assert strength in src.bip39.SUPPORTED_STRENGTH

    # func_has_balance = has_balance_network
    func_has_balance = has_balance_local

    # chunk_bits = 6
    # lim = 2**(11 * (12 - chunk_bits))
    # rng = range(lim)
    lim = 2 ** strength
    rng = gen(lim)

    for i in tqdm(rng, total=lim):
        entropy = tmp_gen_entropy(i, strength, lim)
        mnemonic = src.bip39.generate_mnemonic(entropy)
        assert src.bip39.validate_mnemonic(mnemonic)

        if func_has_balance(mnemonic, db):
            print(f"{i}: {mnemonic}")
            found(mnemonic)

        if i % 100 == 0:
            ping(func_has_balance, db)
            print("ping", i)


def main():
    # db = src.db_handlers.DBSqlite()
    db = src.db_handlers.DBPostgres()

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
