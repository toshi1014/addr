import binascii
import hashlib
import hmac

import bitcoinlib.config.secp256k1
import fastecdsa
import ripemd.ripemd160
from Crypto.Hash import keccak

from . import encoding_tools


SUPPORTED_NETWORK = {"btc-legacy", "btc-segwit", "eth"}


def hash160(string):
    return ripemd.ripemd160.ripemd160(hashlib.sha256(string).digest())


def sha3(seed):
    return keccak.new(digest_bits=256, data=seed).digest()


class AddrGenerator:
    @classmethod
    def addr_btc(cls, hdkey):
        pubkeyhash = hash160(
            binascii.unhexlify(hdkey.public_hex)
        )

        addr = encoding_tools.pubkeyhash2addr(
            pubkeyhash=pubkeyhash,
            prefix=hdkey.prefix,
            encoding=hdkey.encoding,
            witver=0,
        )
        return addr

    @classmethod
    def addr_eth(cls, hdkey):
        nbytes = 32
        bytep = bytes([0x04]) + \
            hdkey.point.x.to_bytes(nbytes, 'big') + \
            hdkey.point.y.to_bytes(nbytes, 'big')

        arg = sha3(bytep[1:])[12:]

        version = '0x'
        addr = version + \
            binascii.hexlify(arg).decode('ascii')

        return addr


class HDKey:
    def __init__(
        self,
        key=None,
        chain=None,
        depth=None,
        encoding=None,
        prefix=None,
    ):
        self.key = key
        self.chain = chain
        self.depth = depth
        self.encoding = encoding
        self.prefix = prefix

        self.private_byte = key
        self.secret = int(self.private_byte.hex(), 16)

    @property
    def point(self):
        return fastecdsa.keys.get_public_key(
            int(self.secret), fastecdsa.curve.secp256k1
        )

    @property
    def public_hex(self):
        if self.point.y % 2:
            prefix = "03"
        else:
            prefix = "02"

        return prefix + hex(self.point.x)[2:].zfill(64)

    @classmethod
    def from_seed(cls, seed, encoding, prefix):
        seed = binascii.unhexlify(seed)
        key, chain = cls.key_derivation(seed)

        return cls(
            key=key,
            chain=chain,
            depth=0,
            encoding=encoding,
            prefix=prefix,
        )

    @classmethod
    def key_derivation(cls, seed, chain=None):
        chain = chain if chain else b"Bitcoin seed"
        i = hmac.new(chain, seed, hashlib.sha512).digest()
        return i[:32], i[32:]

    @classmethod
    def child_private(cls, hdkey, index=0, hardened=False):
        if hardened:
            index |= 0x80000000
            seed = b"\0" + hdkey.private_byte + index.to_bytes(4, "big")
        else:
            seed = bytes.fromhex(hdkey.public_hex) + index.to_bytes(4, "big")

        key, chain = HDKey.key_derivation(seed, hdkey.chain)

        key = int.from_bytes(key, "big")
        newkey = (key + hdkey.secret) % bitcoinlib.config.secp256k1.secp256k1_n
        newkey = int.to_bytes(newkey, 32, "big")

        return HDKey(
            key=newkey,
            chain=chain,
            depth=hdkey.depth + 1,
            encoding=hdkey.encoding,
            prefix=hdkey.prefix,
        )

    @classmethod
    def subkey(cls, hdkey, path):
        key = hdkey
        hardened = path[-1] in "'HhPp"
        if hardened:
            path = path[:-1]
        index = int(path)

        key = cls.child_private(
            key, index=index, hardened=hardened)
        return key

    @classmethod
    def seed2address(cls, seed, network):
        assert network in SUPPORTED_NETWORK

        if network == "btc-legacy":
            fullpath = ["44'", "0'", "0'", '0', '0']
            encoding, prefix = "base58", b'\x00'
        elif network == "btc-segwit":
            fullpath = ["84'", "0'", "0'", '0', '0']
            encoding, prefix = "bech32", "bc"
        elif network == "eth":
            fullpath = ["44'", "60'", "0'", '0', '0']
            encoding, prefix = None, None
        else:
            raise ValueError()

        hdkey = cls.from_seed(seed, encoding, prefix)

        for path in fullpath:
            hdkey = HDKey.subkey(
                hdkey=hdkey,
                path=path,
            )

        # addr
        if "btc" in network:
            func_gen_addr = AddrGenerator.addr_btc
        elif network == "eth":
            func_gen_addr = AddrGenerator.addr_eth
        else:
            raise ValueError

        addr = func_gen_addr(hdkey)
        return addr
