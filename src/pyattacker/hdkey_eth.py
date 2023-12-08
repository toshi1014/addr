import base58
import binascii
import hashlib
import hmac
import ripemd.ripemd160
from Crypto.Hash import keccak
from two1.crypto.ecdsa import secp256k1
import fastecdsa


CURVE_N = 115792089237316195423570985008687907852837564279074904382605163141518161494337


def sha3(seed):
    return keccak.new(digest_bits=256, data=seed).digest()


def myhash160(string):
    return ripemd.ripemd160.ripemd160(hashlib.sha256(string).digest())


class PrivateKeyBase:
    def __init__(self, k):
        self.key = k
        self._public_key = None


class PrivateKey(PrivateKeyBase):
    @property
    def public_key(self):
        self._public_key = fastecdsa.keys.get_public_key(
            int(self.key), fastecdsa.curve.secp256k1
        )

        return self._public_key

    def __bytes__(self):
        return self.key.to_bytes(32, 'big')


class PublicKey:
    MAINNET_VERSION = 0x00

    @staticmethod
    def from_point(p):
        return PublicKey(p.x, p.y)

    @staticmethod
    def from_bytes(key_bytes):
        key_type = key_bytes[0]
        x = int.from_bytes(key_bytes[1:33], 'big')
        ys = secp256k1().y_from_x(x)

        last_bit = key_type - 0x2
        for y in ys:
            if y & 0x1 == last_bit:
                break

        return PublicKey(x, y)

    def __init__(self, x, y):
        self.point = fastecdsa.point.Point(
            x, y, curve=fastecdsa.curve.secp256k1)

        self.ripe = myhash160(bytes(self))
        self.ripe_compressed = myhash160(self.compressed_bytes)
        self.keccak = sha3(bytes(self)[1:])

    def address(self, compressed=True, testnet=False):
        version = '0x'
        return version + binascii.hexlify(self.keccak[12:]).decode('ascii')

    def __bytes__(self):
        nbytes = 32
        return bytes([0x04]) + self.point.x.to_bytes(nbytes, 'big') + self.point.y.to_bytes(nbytes, 'big')

    @property
    def compressed_bytes(self):
        nbytes = 32
        return bytes([(self.point.y & 0x1) + 0x02]) + self.point.x.to_bytes(nbytes, 'big')


class HDKey(object):
    @staticmethod
    def from_bytes(b):
        depth = b[4]
        parent_fingerprint = b[5:9]
        index = int.from_bytes(b[9:13], 'big')
        chain_code = b[13:45]
        key_bytes = b[45:78]

        public_key = PublicKey.from_bytes(key_bytes)
        rv = HDPublicKey(
            x=public_key.point.x,
            y=public_key.point.y,
            chain_code=chain_code,
            index=index,
            depth=depth,
            parent_fingerprint=parent_fingerprint
        )

        return rv

    def __init__(self, key, chain_code, index, depth, parent_fingerprint):
        self._key = key
        self.chain_code = chain_code
        self.depth = depth
        self.index = index
        self.parent_fingerprint = parent_fingerprint

    def __bytes__(self):
        version = self.MAINNET_VERSION
        key_bytes = self._key.compressed_bytes \
            if isinstance(self, HDPublicKey) else b'\x00' + bytes(self._key)
        return (version.to_bytes(length=4, byteorder='big') +
                bytes([self.depth]) +
                self.parent_fingerprint +
                self.index.to_bytes(length=4, byteorder='big') +
                self.chain_code +
                key_bytes)


class HDPrivateKey(HDKey, PrivateKeyBase):
    MAINNET_VERSION = 0x0488ADE4

    @staticmethod
    def master_key_from_seed(seed):
        S = binascii.unhexlify(seed)
        I = hmac.new(b"Bitcoin seed", S, hashlib.sha512).digest()
        Il, Ir = I[:32], I[32:]
        parse_Il = int.from_bytes(Il, 'big')
        return HDPrivateKey(key=parse_Il, chain_code=Ir, index=0, depth=0)

    @staticmethod
    def from_parent(parent_key, i):
        hmac_key = parent_key.chain_code
        hmac_data = b'\x00' + \
            bytes(parent_key._key) + i.to_bytes(length=4, byteorder='big')

        I = hmac.new(hmac_key, hmac_data, hashlib.sha512).digest()
        Il, Ir = I[:32], I[32:]

        parse_Il = int.from_bytes(Il, 'big')
        child_key = (parse_Il + parent_key._key.key) % CURVE_N
        child_depth = parent_key.depth + 1
        return HDPrivateKey(
            key=child_key,
            chain_code=Ir,
            index=i,
            depth=child_depth,
        )

    def __init__(self, key, chain_code, index, depth,
                 parent_fingerprint=b'\x00\x00\x00\x00'):
        if index < 0 or index > 0xffffffff:
            raise ValueError("index is out of range: 0 <= index <= 2**32 - 1")

        private_key = PrivateKey(key)
        HDKey.__init__(self, private_key, chain_code, index, depth,
                       parent_fingerprint)
        self._public_key = None

    @property
    def public_key(self):
        if self._public_key is None:
            self._public_key = HDPublicKey(
                x=self._key.public_key.x,
                y=self._key.public_key.y,
                chain_code=self.chain_code,
                index=self.index,
                depth=self.depth,
                parent_fingerprint=self.parent_fingerprint
            )

        return self._public_key


class HDPublicKey(HDKey):
    MAINNET_VERSION = 0x0488B21E

    @staticmethod
    def from_parent(parent_key, i):
        I = hmac.new(parent_key.chain_code,
                     parent_key.compressed_bytes +
                     i.to_bytes(length=4, byteorder='big'),
                     hashlib.sha512).digest()
        Il, Ir = I[:32], I[32:]
        parse_Il = int.from_bytes(Il, 'big')
        temp_priv_key = PrivateKey(parse_Il)
        Ki = temp_priv_key.public_key + parent_key._key.point

        child_depth = parent_key.depth + 1
        return HDPublicKey(
            x=Ki.x,
            y=Ki.y,
            chain_code=Ir,
            index=i,
            depth=child_depth,
        )

    def __init__(self, x, y, chain_code, index, depth,
                 parent_fingerprint=b'\x00\x00\x00\x00'):
        key = PublicKey(x, y)
        HDKey.__init__(self, key, chain_code, index, depth, parent_fingerprint)

    def address(self, compressed=True, testnet=False):
        return self._key.address(True, testnet)

    @property
    def compressed_bytes(self):
        return self._key.compressed_bytes


class HDKeyETH:
    def __init__(self):
        ...

    @classmethod
    def master_key_from_seed(cls, seed):
        S = binascii.unhexlify(seed)
        I = hmac.new(b"Bitcoin seed", S, hashlib.sha512).digest()
        Il, Ir = I[:32], I[32:]
        parse_Il = int.from_bytes(Il, 'big')
        return HDPrivateKey(key=parse_Il, chain_code=Ir, index=0, depth=0)

    @classmethod
    def from_path(cls, root_key, path):
        p = path.rstrip("/").split("/")

        if p[0] == "m":
            p = p[1:]

        keys = [root_key]
        for i in p:
            if isinstance(i, str):
                hardened = i[-1] == "'"
                index = int(i[:-1], 0) | 0x80000000 if hardened else int(i, 0)
            k = keys[-1]
            klass = k.__class__
            keys.append(klass.from_parent(k, index))

        return keys

    @classmethod
    def create_address(cls, network='btctest', xpub=None, child=None, path=0):
        acct_pub_key = HDKey.from_bytes(base58.b58decode_check(xpub))

        keys = cls.from_path(
            acct_pub_key, '{change}/{index}'.format(change=path, index=child))

        res = {
            "path": "m/" + str(acct_pub_key.index) + "/" + str(keys[-1].index),
            "bip32_path": "m/44'/60'/0'/" + str(acct_pub_key.index) + "/" + str(keys[-1].index),
            "address": keys[-1].address()
        }

        res["xpublic_key"] = base58.b58encode_check(bytes(keys[-1]))

        return res

    @classmethod
    def seed2address(cls, seed, network='btctest', children=1, witness_type=None):
        wallet = {
            "coin": "ETH",
            "seed": seed,
            "children": []
        }

        master_key = cls.master_key_from_seed(seed)
        root_keys = cls.from_path(master_key, "m/44'/60'/0'")
        acct_pub_key = root_keys[-1].public_key

        wallet["xpublic_key"] = base58.b58encode_check(bytes(acct_pub_key))

        wallet["address"] = cls.create_address(
            network=network.upper(),
            xpub=wallet["xpublic_key"],
            child=0,
            path=0,
        )["address"]

        for child in range(children):
            child_wallet = cls.create_address(
                network=network.upper(),
                xpub=wallet["xpublic_key"],
                child=child,
                path=0,
            )
            wallet["children"].append({
                "address": child_wallet["address"],
                "xpublic_key": child_wallet["xpublic_key"],
                "path": "m/" + str(child),
                "bip32_path": "m/44'/60'/0'/" + str(child),
            })

        return wallet["address"]
