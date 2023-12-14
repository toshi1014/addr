import binascii
import copy
import hashlib
import hmac

import bitcoinlib.config.secp256k1
import fastecdsa
import ripemd.ripemd160

import encoding_tools


SUPPORTED_WITNESS_TYPES = {"legacy", "segwit"}
SUPPORTED_NETWORKS = {"btc", "eth"}


def hash160(string):
    return ripemd.ripemd160.ripemd160(hashlib.sha256(string).digest())


class HDKeyBTC:
    def __init__(
        self,
        key=None,
        chain=None,
        child_index=None,
        depth=None,
        witness_type=None,
        encoding=None,
        network=None,
    ):
        self.key = key
        self.chain = chain
        self.child_index = child_index
        self.depth = depth
        self.witness_type = witness_type
        self.encoding = encoding
        self.network = network

        self.private_byte = key
        self.secret = int(self.private_byte.hex(), 16)

        p = fastecdsa.keys.get_public_key(
            int(self.secret), fastecdsa.curve.secp256k1
        )
        if p.y % 2:
            prefix = "03"
        else:
            prefix = "02"

        self.public_hex = prefix + hex(p.x)[2:].zfill(64)
        self.public_byte = bytes.fromhex(self.public_hex)

    @classmethod
    def key_derivation(cls, seed, chain=None):
        chain = chain if chain else b"Bitcoin seed"
        i = hmac.new(chain, seed, hashlib.sha512).digest()
        key = i[:32]
        chain = i[32:]
        return key, chain

    @classmethod
    def from_seed(cls, seed):
        seed = binascii.unhexlify(seed)
        key, chain = cls.key_derivation(seed)

        return cls(
            key=key,
            chain=chain,
            depth=0,
        )

    @classmethod
    def subkey_for_path(cls, hdkey, path, network=None):
        path = path.split("/")
        key = hdkey
        for item in path:
            hardened = item[-1] in "'HhPp"
            if hardened:
                item = item[:-1]
            index = int(item)
            key = cls.child_private(
                key, index=index, hardened=hardened, network=network)
        return key

    @classmethod
    def child_private(cls, hdkey, index=0, hardened=False, network=None):
        if hardened:
            index |= 0x80000000
            data = b"\0" + hdkey.private_byte + index.to_bytes(4, "big")
        else:
            data = hdkey.public_byte + index.to_bytes(4, "big")

        key, chain = HDKeyBTC.key_derivation(data, hdkey.chain)
        key = int.from_bytes(key, "big")

        newkey = (key + hdkey.secret) % bitcoinlib.config.secp256k1.secp256k1_n
        newkey = int.to_bytes(newkey, 32, "big")

        return HDKeyBTC(
            key=newkey,
            chain=chain,
            depth=hdkey.depth + 1,
            child_index=index,
            witness_type=hdkey.witness_type,
            encoding=hdkey.encoding,
            network=network,
        )

    @classmethod
    def path_expand(
        cls,
        path,
        path_template=None,
        account_id=0,
        cosigner_id=0,
        purpose=44,
        address_index=0,
        change=0,
        witness_type="legacy",
        network="bitcoin",
    ):
        poppath = copy.deepcopy(path)
        wallet_key_path = path_template
        new_path = []
        for pi in wallet_key_path[::-1]:
            new_path.append(
                poppath.pop() if len(poppath) else pi
            )
        new_path = new_path[::-1]

        script_type_id = 1 if witness_type == 'p2sh-segwit' else 2
        var_defaults = {
            'network': network,
            'account': account_id,
            'purpose': purpose,
            'coin_type': 0,
            'script_type': script_type_id,
            'cosigner_index': cosigner_id,
            'change': change,
            'address_index': address_index
        }
        npath = new_path
        for i, pi in enumerate(new_path):
            pi = str(pi)
            if pi in "mM":
                continue
            hardened = False
            varname = pi
            if pi[-1:] == "'" or (pi[-1:] in "HhPp" and pi[:-1].isdigit()):
                varname = pi[:-1]
                hardened = True
            if path_template[i][-1:] == "'":
                hardened = True
            new_varname = str(var_defaults[varname]) \
                if varname in var_defaults else varname
            npath[i] = new_varname + ("'" if hardened else '')
        return npath

    @classmethod
    def seed2address(cls, seed, witness_type, network="btc"):
        assert witness_type in SUPPORTED_WITNESS_TYPES
        assert network in SUPPORTED_NETWORKS

        hdkey = cls.from_seed(seed)

        path = [0, 0]
        path_template = [
            "m",
            "purpose'",
            "coin_type'",
            "account'",
            "change",
            "address_index",
        ]
        address_index = 0
        network = "bitcoin"

        if witness_type == "legacy":
            encoding = "base58"
            purpose = 44
            prefix = b'\x00'
        elif witness_type == "segwit":
            encoding = "bech32"
            purpose = 84
            prefix = "bc"
        else:
            raise ValueError(encoding)

        fullpath = cls.path_expand(
            path=path,
            path_template=path_template,
            account_id=0,
            cosigner_id=None,
            purpose=purpose,
            address_index=address_index,
            change=0,
            witness_type=witness_type,
            network=network,
        )

        newpath = "m"
        for lvl in fullpath[1:]:
            hdkey = HDKeyBTC.subkey_for_path(
                hdkey=hdkey,
                path=lvl,
                network=network,
            )

            newpath += "/" + lvl
            key_name = "%s %s" % (
                path_template[len(newpath.split("/"))-1], lvl)
            key_name = key_name.replace("'", "").replace("_", " ")

        pubkeyhash = hash160(
            binascii.unhexlify(hdkey.public_hex)
        )

        address = encoding_tools.pubkeyhash2addr(
            pubkeyhash=pubkeyhash,
            prefix=prefix,
            encoding=encoding,
            witver=0,
        )
        return address
