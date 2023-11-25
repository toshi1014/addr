import hashlib


CODE_STRINGS = {
    2: b'01',
    3: b' ,.',
    10: b'0123456789',
    16: b'0123456789abcdef',
    32: b'abcdefghijklmnopqrstuvwxyz234567',
    58: b'123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz',
    256: b''.join([bytes((csx,)) for csx in range(256)]),
    'bech32': b'qpzry9x8gf2tvdw0s3jn54khce6mua7l'
}


def convertbits(data, frombits, tobits, pad=True):
    acc = 0
    bits = 0
    ret = []
    maxv = (1 << tobits) - 1
    max_acc = (1 << (frombits + tobits - 1)) - 1

    for value in data:
        if value < 0 or (value >> frombits):
            return None
        acc = ((acc << frombits) | value) & max_acc
        bits += frombits
        while bits >= tobits:
            bits -= tobits
            ret.append((acc >> bits) & maxv)

    if pad:
        if bits:
            ret.append((acc << (tobits - bits)) & maxv)
    elif bits >= frombits or ((acc << (tobits - bits)) & maxv):
        return None
    return ret


def _array_to_codestring(array, base):
    codebase = CODE_STRINGS[base]
    codestring = ""
    for i in array:
        codestring += chr(codebase[i])
    return codestring


def _bech32_polymod(values):
    generator = [0x3b6a57b2, 0x26508e6d, 0x1ea119fa, 0x3d4233dd, 0x2a1462b3]
    chk = 1
    for value in values:
        top = chk >> 25
        chk = (chk & 0x1ffffff) << 5 ^ value
        for i in range(5):
            chk ^= generator[i] if ((top >> i) & 1) else 0
    return chk


def pubkeyhash2addr_bech32(pubkeyhash, prefix='bc', witver=0, separator='1', checksum_xor=1):
    pubkeyhash = list(pubkeyhash)
    data = [witver] + convertbits(pubkeyhash, 8, 5)

    # Expand the HRP into values for checksum computation
    hrp_expanded = [ord(x) >> 5 for x in prefix] + [0] + \
        [ord(x) & 31 for x in prefix]
    polymod = _bech32_polymod(
        hrp_expanded + data + [0, 0, 0, 0, 0, 0]
    ) ^ checksum_xor
    checksum = [(polymod >> 5 * (5 - i)) & 31 for i in range(6)]

    return prefix + separator + _array_to_codestring(data, 'bech32') + _array_to_codestring(checksum, 'bech32')


def base58encode(inp):
    origlen = len(inp)
    inp = inp.lstrip(b'\0')
    padding_zeros = origlen - len(inp)
    code_str = CODE_STRINGS[58].decode()
    acc = int.from_bytes(inp, 'big')

    string = ''
    while acc:
        acc, idx = divmod(acc, 58)
        string = code_str[idx:idx + 1] + string
    return '1' * padding_zeros + string


def pubkeyhash2addr_base58(pubkeyhash, prefix=b'\x00'):
    key = prefix + pubkeyhash
    addr256 = key + hashlib.sha256(
        hashlib.sha256(key).digest()
    ).digest()[:4]
    return base58encode(addr256)


def pubkeyhash2addr(pubkeyhash, encoding, prefix=None, witver=0):
    if encoding == "base58":
        return pubkeyhash2addr_base58(pubkeyhash, prefix)
    elif encoding == 'bech32':
        return pubkeyhash2addr_bech32(pubkeyhash, prefix, witver)
    else:
        raise ValueError(encoding)
