#include "bip39.hpp"

#include "hash.hpp"

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
    std::stringstream ss;
    ss << std::hex << entropy;
    std::cout << hash::hexSha256(ss.str()) << '\n';

    return "MNEMONIC";
}

}  // namespace bip39
