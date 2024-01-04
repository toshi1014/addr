#include "hdkey.hpp"

namespace hdkey {

EccPoint::EccPoint(const std::string key) : key(key) {}

HDKey::HDKey(uint256_t key, std::string chain_code, uint32_t index,
             uint32_t depth, std::string parent_fingerprint)
    : key(key),
      chain_code(chain_code),
      index(index),
      depth(depth),
      parent_fingerprint(parent_fingerprint) {}

HDPublicKey HDPublicKey::from_parent(HDPublicKey parent_key, const uint32_t i) {
    return parent_key;
}

HDPrivateKey::HDPrivateKey(uint256_t key, std::string chain_code,
                           uint32_t index, uint32_t depth,
                           std::string parent_fingerprint)
    : HDKey(key, chain_code, index, depth, parent_fingerprint) {
    EccPoint private_key{"A"};
}

HDPrivateKey HDPrivateKey::from_parent(HDPrivateKey parent_key,
                                       const uint32_t i) {
    const std::string hmac_key = parent_key.chain_code;

    const std::string hmac_data = "00" +
                                  hash::dec2hex<uint256_t>(parent_key.key) +
                                  hash::dec2hex_naive(i);

    // hmac
    const EVP_MD* hash_func = EVP_sha512();
    const std::string I = hash::hexHmacHexKey(hmac_data, hmac_key, hash_func,
                                              SHA512_DIGEST_LENGTH);
    const std::string Il = I.substr(0, SHA512_DIGEST_LENGTH);
    const std::string Ir = I.substr(SHA512_DIGEST_LENGTH, SHA512_DIGEST_LENGTH);

    const uint256_t child_key =
        (hash::hex2dec<uint256_t>(Il) + parent_key.key) % CURVE_N;


    std::cout << (hmac_data.length()) << "\n" << std::endl;
    return HDPrivateKey(child_key, Ir, i, parent_key.depth + 1, "A");
}
// 1c56ca9209dc460d57de442c18b692fd2fd60134b86c5247afdcbd1b8f68ff150231397e17b0dd61dd2e427172ed2cd739cbd6f3400f3e50fc385d46a0c237be
// e9054e7cde12b90ab0d33491c803be82c500497eb159f0c48469d98bc8d9e8587ddc4f0c1f0d9f9cc456449db412c24301bc90b538b72173eb1f981cd05c41fd
// 21a24456eb1e702de1c40bdcd2923db279534523f30168dd38df85ae48a5f095b82b7dfd98b24191418a59eb0c785d3c3bc26304874ecc5b70656e1b8caddd17

// 1c56ca9209dc460d57de442c18b692fd2fd60134b86c5247afdcbd1b8f68ff150231397e17b0dd61dd2e427172ed2cd739cbd6f3400f3e50fc385d46a0c237be
// e9054e7cde12b90ab0d33491c803be82c500497eb159f0c48469d98bc8d9e8587ddc4f0c1f0d9f9cc456449db412c24301bc90b538b72173eb1f981cd05c41fd
// eefd799c503b857020cfcfc8495ec86523c7018c67b11f0883bb9efa365b9cf8cfa0a20a1a2ee3ac3decb9c40341edbacdc7a1f3ada139aea1aa6fcf0947be6d

HDPrivateKey HDPrivateKey::master_key_from_seed(const std::string& seed) {
    std::string key = "Bitcoin seed";
    const EVP_MD* hash_func = EVP_sha512();

    std::string I = hash::hexHmac(seed, key, hash_func, SHA512_DIGEST_LENGTH);
    std::string Il = I.substr(0, SHA512_DIGEST_LENGTH);
    std::string Ir = I.substr(SHA512_DIGEST_LENGTH, SHA512_DIGEST_LENGTH);

    return HDPrivateKey(hash::hex2dec<uint256_t>(Il), Ir, 0, 1, "A");
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

    return "addr";
}

}  // namespace hdkey
