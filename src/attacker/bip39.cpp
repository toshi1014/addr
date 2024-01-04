#include "bip39.hpp"

#include "hash.hpp"
#include "wordlist.hpp"

namespace bip39 {

const char DELIMITER = ' ';

namespace entropy {

uint128_t increment(const uint32_t i) { return 1111; }

uint128_t CSPRNG(const uint32_t i) {
    uint128_t tmp;

    getrandom(&tmp, sizeof(uint128_t), GRND_NONBLOCK);
    return tmp;
}

}  // namespace entropy

std::string generate_mnemonic(const uint128_t entropy) {
    std::stringstream entropy_hex;
    entropy_hex << std::hex << entropy;

    const std::string hex_hash = hash::hexSha256(entropy_hex.str());

    std::string b = hash::hex2bin(entropy_hex.str());
    const std::string checksum = hash::hex2bin(hex_hash).substr(0, 4);

    b += checksum;

    std::stringstream ss_mnemonic;
    for (uint32_t i = 0; i < b.length() / 11; i++) {
        ss_mnemonic << WORDLIST[hash::bin2dec(b.substr(i * 11, 11))] + " ";
    }

    std::string mnemonic = ss_mnemonic.str();
    mnemonic.pop_back();  // remove last space
    return mnemonic;
}

std::string mnemonic2seed(const std::string& mnemonic) {
    return hash::PBKDF2_HMAC_SHA_512(&(mnemonic[0]), "mnemonic",
                                     ITER_PBKDF2_HMAC, SIZE_PBKDF2_HMAC);
}

}  // namespace bip39
