#include "hdkey.hpp"

#include "address.hpp"

namespace hdkey {

HDKey::HDKey(uint512_t key, collections::HexArray chain_code, uint32_t depth,
             Encoding encoding, std::string prefix)
    : key(key),
      chain_code(chain_code),
      depth(depth),
      encoding(encoding),
      prefix(prefix) {}

const std::string HDKey::get_key_hex() const {
    std::stringstream ss;
    ss << std::setw(KEY_SIZE) << std::setfill('0')
       << hash::dec2hex<uint512_t>(this->key);
    return ss.str();
};

HDKey HDKey::from_seed(const collections::HexArray& seed_hexarr,
                       const Encoding& encoding, const std::string& prefix) {
    const std::string key = "Bitcoin seed";
    const EVP_MD* hash_func = EVP_sha512();

    std::string I =
        hash::hexHmac(seed_hexarr, key, hash_func, SHA512_DIGEST_LENGTH)
            ->to_str();
    std::string Il = I.substr(0, SHA512_DIGEST_LENGTH);
    std::string Ir = I.substr(SHA512_DIGEST_LENGTH, SHA512_DIGEST_LENGTH);

    return HDKey(hash::hex2dec<uint512_t>(Il),
                 collections::HexArray::from_str(Ir), 0, encoding, prefix);
}

HDKey HDKey::child_private(HDKey& hdkey, uint32_t index, bool hardened) {
    std::string seed;

    if (hardened) {
        index |= 2147483648;  // 2147483648 is 0x80000000
        seed = "00" + hdkey.get_key_hex() + hash::dec2hex_naive(index);

    } else {
        public_key::PublicKey pubkey{hdkey.key};
        seed = pubkey.compressed() + hash::dec2hex_naive(index) + "0000000";
    }

    collections::HexArray seed_hexarr = collections::HexArray::from_str(seed);

    // hmac
    const EVP_MD* hash_func = EVP_sha512();
    const std::string I = hash::hexHmacHexKey(seed_hexarr, hdkey.chain_code,
                                              hash_func, SHA512_DIGEST_LENGTH)
                              ->to_str();
    const std::string Il = I.substr(0, SHA512_DIGEST_LENGTH);
    const std::string Ir = I.substr(SHA512_DIGEST_LENGTH, SHA512_DIGEST_LENGTH);

    const uint512_t child_key =
        (hash::hex2dec<uint512_t>(Il) + hdkey.key) % CURVE_N;

    return HDKey(child_key, collections::HexArray::from_str(Ir),
                 hdkey.depth + 1, hdkey.encoding, hdkey.prefix);
}

HDKey HDKey::subkey(HDKey& hdkey, std::string path) {
    bool hardened = false;
    if (path[path.length() - 1] == '\'') {
        hardened = true;
        path = path.substr(0, path.length() - 1);
    }

    return HDKey::child_private(hdkey, stoi(path), hardened);
}

std::string HDKey::seed2addr(const collections::HexArray& seed_hexarr) {
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

    HDKey hdkey = HDKey::from_seed(seed_hexarr, encoding, prefix);

    for (const std::string& path : fullpath) hdkey = HDKey::subkey(hdkey, path);

    return func_addr_gen(fullpath, hdkey);
}

}  // namespace hdkey
