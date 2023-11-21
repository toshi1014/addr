import binascii
import hashlib
import base58
import ecdsa
from ripemd import ripemd160


# ref.
#  * https://gobittest.appspot.com/PrivateKey
#  * https://en.bitcoin.it/wiki/Private_key


def hash(val, func_hash=hashlib.sha256):
    return binascii.hexlify(func_hash(binascii.unhexlify(val)).digest())


def prikey2pubkey(private_key, curve=ecdsa.SECP256k1):
    # first byte:
    #     "02" => y even
    #     "03" => y odd
    #     "04" => uncompressed

    private_key_obj = ecdsa.SigningKey.from_string(
        binascii.unhexlify(private_key),
        curve=curve,
    )
    return private_key_obj.verifying_key.to_string(encoding="compressed").hex()


def pubkey2addr(public_key, testnet):
    # ref. https://en.bitcoin.it/wiki/Technical_background_of_version_1_Bitcoin_addresses

    # 1. public key

    # 2. sha256
    hashed = hash(public_key)

    # 3. ripemd160
    r = ripemd160.new()
    r.update(binascii.unhexlify(hashed))
    ripemd = binascii.hexlify(r.digest())

    # 4. pad ver
    byte_ver = b"6f" if testnet else b"00"
    extended_ripemd = byte_ver + ripemd

    # 5. sha256
    hashed2 = hash(extended_ripemd)

    # 6. sha256 again
    hashed3 = hash(hashed2)

    # 7. checksum
    checksum = hashed3[:8]

    # 8. 25-byte addr
    addr25 = extended_ripemd + checksum

    # 9. addr
    addr = base58.b58encode(binascii.unhexlify(addr25))

    return addr.decode()


def prikey2wif(private_key, testnet, compressed):
    # ref. https://en.bitcoin.it/wiki/Wallet_import_format

    # 1. private_key

    # 2. pad ver
    byte_pre = b"ef" if testnet else b"80"
    byte_suf = b"01" if compressed else b""
    extended = byte_pre + private_key.encode() + byte_suf

    # 3. sha256
    hashed1 = hash(extended)

    # 4. sha256 again
    hashed2 = hash(hashed1)

    # 5. checksum
    checksum = hashed2[:8]

    # 6. extended + checksum
    with_checksum = extended + checksum

    # 7. wif
    wif = base58.b58encode(binascii.unhexlify(with_checksum))

    return wif.decode()


def wif2prikey(wif):
    if len(wif) == 51:      # uncompressed public key
        compressed = False

        if wif[0] == "5":
            ...             # mainnet
        elif wif[0] == "9":
            ...             # testnet
        else:
            raise ValueError(f"Wrong version: {wif[0]}")

    elif len(wif) == 52:    # compressed public key
        compressed = True
        if wif[0] in {"L", "K"}:
            ...             # mainnet
        elif wif[0] == "c":
            ...             # testnet
        else:
            raise ValueError(f"Wrong version: {wif[0]}")
    else:
        raise ValueError(f"Bad length: {len(wif)}")

    # 1. wif

    # 2. decode base58check
    dec = binascii.hexlify(base58.b58decode(wif))

    # 3. drop checksum
    without_checksum = dec[:-8]

    # 4. drop fst byte (last too if comppressed)
    idx_last = len(without_checksum) - \
        2 if compressed else len(without_checksum)
    prikey = without_checksum[2:idx_last]

    return prikey.decode()


def is_valid_wif(wif):
    # 1. wif

    # 2. decode base58check
    dec = binascii.hexlify(base58.b58decode(wif))

    # 3. drop checksum
    without_checksum = dec[:-8]

    # 4. sha256
    hashed1 = hash(without_checksum)

    # 5. sha256 again
    hashed2 = hash(hashed1)

    # 6. checksum
    checksum = hashed2[:8]

    # 7. expected checksum
    expected_checksum = dec[-8:]

    return checksum.hex() == expected_checksum.hex()
