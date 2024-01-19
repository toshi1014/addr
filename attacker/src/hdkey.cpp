#include "hdkey.hpp"

namespace hdkey {

AHDKey::AHDKey(uint512_t key, std::string chain_code, uint32_t depth,
               Encoding encoding, std::string prefix)
    : key(key),
      chain_code(chain_code),
      depth(depth),
      encoding(encoding),
      prefix(prefix) {}

AHDKey AHDKey::from_seed(const std::string& seed, const Encoding& encoding,
                         const std::string& prefix) {
    const std::string key = "Bitcoin seed";
    const EVP_MD* hash_func = EVP_sha512();

    std::string I = hash::hexHmac(seed, key, hash_func, SHA512_DIGEST_LENGTH);
    std::string Il = I.substr(0, SHA512_DIGEST_LENGTH);
    std::string Ir = I.substr(SHA512_DIGEST_LENGTH, SHA512_DIGEST_LENGTH);

    return AHDKey(hash::hex2dec<uint512_t>(Il), Ir, 0, encoding, prefix);
}

AHDKey AHDKey::child_private(AHDKey& hdkey, uint32_t index, bool hardened) {
    std::string seed;

    if (hardened) {
        index |= 2147483648;  // 2147483648 is 0x80000000
        seed = "00" + hash::dec2hex<uint512_t>(hdkey.key) +
               hash::dec2hex_naive(index);
    } else {
        seed = "pubbyte" + hash::dec2hex_naive(index);
    }
    std::cout << seed << std::endl;

    // hmac
    const EVP_MD* hash_func = EVP_sha512();
    const std::string I = hash::hexHmacHexKey(seed, hdkey.chain_code, hash_func,
                                              SHA512_DIGEST_LENGTH);
    const std::string Il = I.substr(0, SHA512_DIGEST_LENGTH);
    const std::string Ir = I.substr(SHA512_DIGEST_LENGTH, SHA512_DIGEST_LENGTH);

    const uint512_t child_key =
        (hash::hex2dec<uint512_t>(Il) + hdkey.key) % CURVE_N;

    return AHDKey(child_key, Ir, hdkey.depth + 1, hdkey.encoding, hdkey.prefix);
}

AHDKey AHDKey::subkey(AHDKey& hdkey, std::string path) {
    bool hardened = false;
    if (path[path.length() - 1] == '\'') {
        hardened = true;
        path = path.substr(0, path.length() - 1);
    }

    return AHDKey::child_private(hdkey, stoi(path), hardened);
}

std::string AHDKey::seed2addr(const std::string& seed) {
    Network network = BtcLegacy;
    Path fullpath;
    Encoding encoding;
    std::string prefix;

    if (network == BtcLegacy) {
        fullpath = {"44'", "0'", "0'", "0", "0"};
        encoding = Encoding::base58;
        prefix = "00";
    } else if (network == BtcSegwit) {
        fullpath = {"84'", "0'", "0'", "0", "0"};
        encoding = Encoding::bech32;
        prefix = "bc";
    } else if (network == Eth) {
        fullpath = {"44'", "60'", "0'", "0", "0"};
        // encoding = NULL;
        prefix = nullptr;
    } else {
        throw std::invalid_argument("bad network");
    }

    AHDKey hdkey = AHDKey::from_seed(seed, encoding, prefix);

    for (const std::string& path : fullpath)
        hdkey = AHDKey::subkey(hdkey, path);

    return "AA";
}

}  // namespace hdkey

namespace hdkey {

// EccPoint
EccPoint::EccPoint(const std::string key) : key(key) {}

// PublicKey
PublicKey::PublicKey(const uint512_t x, const uint512_t y) {}

// HDKey
HDKey::HDKey(uint512_t key, std::string chain_code, uint32_t index,
             uint32_t depth, std::string parent_fingerprint)
    : key(key),
      chain_code(chain_code),
      index(index),
      depth(depth),
      parent_fingerprint(parent_fingerprint) {}

// HDPublicKey
HDPublicKey::HDPublicKey(uint512_t x, uint512_t y, std::string chain_code,
                         uint32_t index, uint32_t depth,
                         std::string parent_fingerprint)
    : HDKey(x + y, chain_code, index, depth, parent_fingerprint) {}

HDPublicKey HDPublicKey::from_parent(HDPublicKey parent_key, const uint32_t i) {
    return parent_key;
}

// HDPrivateKey
HDPrivateKey::HDPrivateKey(uint512_t key, std::string chain_code,
                           uint32_t index, uint32_t depth,
                           std::string parent_fingerprint)
    : HDKey(key, chain_code, index, depth, parent_fingerprint) {
    EccPoint private_key{"A"};
}

HDPrivateKey HDPrivateKey::master_key_from_seed(const std::string& seed) {
    std::string key = "Bitcoin seed";
    const EVP_MD* hash_func = EVP_sha512();

    std::string I = hash::hexHmac(seed, key, hash_func, SHA512_DIGEST_LENGTH);
    std::string Il = I.substr(0, SHA512_DIGEST_LENGTH);
    std::string Ir = I.substr(SHA512_DIGEST_LENGTH, SHA512_DIGEST_LENGTH);

    return HDPrivateKey(hash::hex2dec<uint512_t>(Il), Ir, 0, 1, "A");
}

HDPrivateKey HDPrivateKey::from_parent(HDPrivateKey parent_key,
                                       const uint32_t i) {
    const std::string hmac_key = parent_key.chain_code;

    const std::string hmac_data = "00" +
                                  hash::dec2hex<uint512_t>(parent_key.key) +
                                  hash::dec2hex_naive(i);

    // hmac
    const EVP_MD* hash_func = EVP_sha512();
    const std::string I = hash::hexHmacHexKey(hmac_data, hmac_key, hash_func,
                                              SHA512_DIGEST_LENGTH);
    const std::string Il = I.substr(0, SHA512_DIGEST_LENGTH);
    const std::string Ir = I.substr(SHA512_DIGEST_LENGTH, SHA512_DIGEST_LENGTH);

    const uint512_t child_key =
        (hash::hex2dec<uint512_t>(Il) + parent_key.key) % CURVE_N;

    return HDPrivateKey(child_key, Ir, i, parent_key.depth + 1, "A");
}

HDPublicKey HDPrivateKey::public_key() {
    // COMBAK:
    return HDPublicKey(1, 2, "A", 12, 1, "A");
}

template <typename T>
T HDKeyEth::from_path(T root_key, Path path) {
    T last_key = root_key;

    for (const std::string& p : path) {
        long index;

        if (p[p.length() - 1] == '\'') {
            index =
                std::atoi(p.c_str()) | 2147483648;  // 2147483648 == 0x80000000
        } else {
            index = std::atoi(p.c_str());
        }
        last_key = T::from_parent(last_key, index);
    }

    return last_key;
}

std::string HDKeyEth::seed2addr(const std::string& seed) {
    Wallet wallet;
    wallet.coin = "ETH";
    wallet.seed = seed;
    wallet.children = {};
    Path path = {"44'", "60'", "0'"};

    HDPrivateKey master_key = HDPrivateKey::master_key_from_seed(seed);
    HDPrivateKey root_keys = HDKeyEth::from_path(master_key, path);
    HDPublicKey pkey = root_keys.public_key();

    return "addr";
}

}  // namespace hdkey
