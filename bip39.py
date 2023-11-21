import hashlib
import itertools
import os
import random


# ref. https://en.bitcoin.it/wiki/BIP_0039
#  * https://github.com/trezor/python-mnemonic


PBKDF2_ROUNDS = 2048
SUPPORTED_STRENGTH = {128, 256}
SUPPORTED_WORD_LENGTH = {12, 15, 18, 21, 24}

with open("wordlist.txt", mode="r", encoding="utf-8") as f:
    WORDLIST = f.read().split("\n")[:-1]


def to_clipboard(string):
    os.system(f"echo {str(string)} | xsel --clipboard --input")


def gen_entropy(strength):
    assert strength in SUPPORTED_STRENGTH
    return os.urandom(strength // 8)


def generate_mnemonic(entropy):
    DELIMITER = " "

    hex_hash = hashlib.sha256(entropy).hexdigest()

    bin_hash = bin(
        int.from_bytes(entropy, byteorder="big")
    )[2:].zfill(len(entropy) * 8)
    checksum = bin(int(hex_hash, 16))[2:].zfill(256)[:len(entropy) * 8 // 32]

    b = bin_hash + checksum

    indices = [
        int(b[i * 11: (i + 1) * 11], 2)
        for i in range(len(b) // 11)
    ]

    return DELIMITER.join([
        WORDLIST[i] for i in indices
    ])


def check(mnemonic):
    try:
        words = mnemonic.split(" ")

        if not len(words) in SUPPORTED_WORD_LENGTH:
            return False

        indices = map(
            lambda x: bin(WORDLIST.index(x))[2:].zfill(11), words
        )
        b = "".join(indices)

    except Exception:
        return False

    length = len(b)
    d = b[: length // 33 * 32]
    checksum = b[-length // 33:]
    nd = int(d, 2).to_bytes(length // 33 * 4, byteorder="big")
    expected_checksum = bin(
        int(hashlib.sha256(nd).hexdigest(), 16)
    )[2:].zfill(256)[: length // 33]
    return checksum == expected_checksum


def mnemonics2seed(mnemonic, passphrase=""):
    salt = "mnemonic" + passphrase

    streched = hashlib.pbkdf2_hmac(
        hash_name="sha512",
        password=mnemonic.encode("utf-8"),
        salt=salt.encode("utf-8"),
        iterations=PBKDF2_ROUNDS,
    )
    return streched[:64].hex()


def recover_entropy(mnemonic):
    words = mnemonic.split(" ")
    assert len(words) in SUPPORTED_WORD_LENGTH

    bit_len = len(words) * 11
    b = [False] * bit_len
    for i, word in enumerate(words):
        assert word in WORDLIST
        for j in range(11):
            b[i * 11 + j] = (WORDLIST.index(word) & (1 << (10 - j))) != 0

    checksum_length = bit_len // 33
    entropy_length = bit_len - checksum_length

    # extract entropy
    entropy = bytearray(entropy_length // 8)

    for i in range(entropy.__len__()):      # __len__: avoid lint warning
        for j in range(8):
            if b[i * 8 + j]:
                entropy[i] |= 1 << (7 - j)

    # checksum
    hashed = hashlib.sha256(entropy).digest()
    bb = list(
        itertools.chain.from_iterable(
            [h & (1 << (7 - i)) != 0 for i in range(8)] for h in hashed
        )
    )
    for i in range(checksum_length):
        assert b[entropy_length + i] == bb[i]

    return bytes(entropy)


def tmp_gen_entropy(i, strength, lim):
    entropy = (i).to_bytes(strength, byteorder="big")[-strength//8:]
    # entropy = random.randint(1, lim).to_bytes(strength, byteorder="big")[-strength//8:]
    # entropy = os.urandom(strength // 8)
    return entropy


def get_balance(mnemonic):
    return False


def find(strength):
    assert strength in SUPPORTED_STRENGTH
    lim = 2 ** strength

    for i in range(lim):
        entropy = tmp_gen_entropy(i, strength, lim)
        mnemonic = generate_mnemonic(entropy)
        assert check(mnemonic)

        if get_balance(mnemonic):
            print(i, "\t", mnemonic)
            with open("found.txt", mode="a", encoding="utf-8") as f:
                f.write(mnemonic + "\n")


def main():
    entropy = gen_entropy(strength=128)
    mnemonic = generate_mnemonic(entropy)
    seed = mnemonics2seed(mnemonic)
    recovered_entropy = recover_entropy(mnemonic)

    assert check(mnemonic)
    assert entropy == recovered_entropy

    print("mnemonic:\t", mnemonic)
    print("seed:\t", seed)
    print("entropy:\t", entropy)
    print("recovered:\t", recovered_entropy)

    to_clipboard(mnemonic)


# find(strength=128)
main()

# * final check on metamask
# * add diff btc/eth
# * check actual balance wallet sometimes
# * seed to addr

# Test
#  * https://allprivatekeys.com/mnemonic-code-converter
#  * https://mnemonic-phrase-generator.com/
