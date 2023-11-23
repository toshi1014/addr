import os
import random
from bitcoinlib.wallets import Wallet, wallet_delete_if_exists
from tqdm import tqdm
import bip39
import utils


def get_balance(mnemonic):
    wallet_name = "Wallet1"
    # mnemonic = "real crater virtual there brush blush unable bone pelican hotel since elite"

    if wallet_delete_if_exists(wallet_name):
        ...

    wallet = Wallet.create(
        name=wallet_name,
        keys=mnemonic,
        network="bitcoin",
    )

    return wallet.balance()


def tmp_gen_entropy(i, strength, lim):
    # count up
    # entropy = (i).to_bytes(strength, byteorder="big")[-strength//8:]

    # PRNG
    # entropy = random.randint(1, lim).to_bytes(strength, byteorder="big")[-strength//8:]

    # CSPRNG
    entropy = os.urandom(strength // 8)
    return entropy


def gen(lim):
    for g in range(lim):
        yield g


@utils.with_timer(template="Delta: {time} (s)")
def run(strength):
    assert strength in bip39.SUPPORTED_STRENGTH
    lim = 2 ** strength

    # chunk_bits = 6
    # lim = 2**(11 * (12 - chunk_bits))
    # rng = range(lim)
    rng = gen(lim)

    for i in tqdm(rng, total=lim):
        entropy = tmp_gen_entropy(i, strength, lim)
        mnemonic = bip39.generate_mnemonic(entropy)
        assert bip39.check(mnemonic)

        if get_balance(mnemonic):
            print(f"{i}: {mnemonic}")
            utils.notify(mnemonic)
            with open("found.txt", mode="a", encoding="utf-8") as f:
                f.write(mnemonic + "\n")


run(strength=128)


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
