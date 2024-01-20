#include "hdkey.hpp"

#include "address.hpp"

namespace hdkey {

HDKey::HDKey(uint512_t key, std::string chain_code, uint32_t depth,
             Encoding encoding, std::string prefix)
    : key(key),
      chain_code(chain_code),
      depth(depth),
      encoding(encoding),
      prefix(prefix) {}

HDKey HDKey::from_seed(const std::string& seed, const Encoding& encoding,
                       const std::string& prefix) {
    const std::string key = "Bitcoin seed";
    const EVP_MD* hash_func = EVP_sha512();

    std::string I = hash::hexHmac(seed, key, hash_func, SHA512_DIGEST_LENGTH);
    std::string Il = I.substr(0, SHA512_DIGEST_LENGTH);
    std::string Ir = I.substr(SHA512_DIGEST_LENGTH, SHA512_DIGEST_LENGTH);

    return HDKey(hash::hex2dec<uint512_t>(Il), Ir, 0, encoding, prefix);
}

HDKey HDKey::child_private(HDKey& hdkey, uint32_t index, bool hardened) {
    std::string seed;

    if (hardened) {
        index |= 2147483648;  // 2147483648 is 0x80000000
        seed = "00" + hash::dec2hex<uint512_t>(hdkey.key) +
               hash::dec2hex_naive(index);

    } else {
        public_key::PublicKey pubkey{hdkey.key};
        seed = pubkey.compressed() + hash::dec2hex_naive(index) + "0000000";
    }

    // hmac
    const EVP_MD* hash_func = EVP_sha512();
    const std::string I = hash::hexHmacHexKey(seed, hdkey.chain_code, hash_func,
                                              SHA512_DIGEST_LENGTH);
    const std::string Il = I.substr(0, SHA512_DIGEST_LENGTH);
    const std::string Ir = I.substr(SHA512_DIGEST_LENGTH, SHA512_DIGEST_LENGTH);

    const uint512_t child_key =
        (hash::hex2dec<uint512_t>(Il) + hdkey.key) % CURVE_N;

    return HDKey(child_key, Ir, hdkey.depth + 1, hdkey.encoding, hdkey.prefix);
}

HDKey HDKey::subkey(HDKey& hdkey, std::string path) {
    bool hardened = false;
    if (path[path.length() - 1] == '\'') {
        hardened = true;
        path = path.substr(0, path.length() - 1);
    }

    return HDKey::child_private(hdkey, stoi(path), hardened);
}

std::string HDKey::seed2addr(const std::string& seed) {
    // Network network = BtcLegacy;
    Network network = Eth;

    Path fullpath;
    Encoding encoding;
    std::string prefix;
    const std::string (*func_addr_gen)(const Path, const HDKey&);

    if (network == BtcLegacy) {
        fullpath = {"44'", "0'", "0'", "0", "0"};
        encoding = Encoding::base58;
        prefix = "00";
        func_addr_gen = address::to_btc;
    } else if (network == BtcSegwit) {
        fullpath = {"84'", "0'", "0'", "0", "0"};
        encoding = Encoding::bech32;
        prefix = "bc";
        func_addr_gen = address::to_btc;
    } else if (network == Eth) {
        fullpath = {"44'", "60'", "0'", "0", "0"};
        // encoding = NULL;
        prefix = "";
        func_addr_gen = address::to_eth;
    } else {
        throw std::invalid_argument("bad network");
    }

    HDKey hdkey = HDKey::from_seed(seed, encoding, prefix);

    for (const std::string& path : fullpath) hdkey = HDKey::subkey(hdkey, path);

    return func_addr_gen(fullpath, hdkey);
}

}  // namespace hdkey
