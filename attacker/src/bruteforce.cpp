#include "bruteforce.hpp"

#include <assert.h>

#include <cmath>
#include <iostream>

#include "bip39.hpp"
#include "hdkey.hpp"

namespace bruteforce {

void run(const uint32_t strength) {
    assert(strength == 128 || strength == 256);
    // std::string strLim = "340282366920938463463374607431768211455";
    std::string strLim = "1";
    uint128_t lim(strLim);

    uint128_t (*func_gen_entropy)(uint32_t);
    func_gen_entropy = *bip39::entropy::CSPRNG;

    for (uint32_t i = 0; i < lim; i++) {
        uint128_t entropy = func_gen_entropy(i);
        std::string mnemonic = bip39::generate_mnemonic(entropy);
        std::cout << entropy << std::endl;
    }
}

bool test(const uint128_t entropy, const std::string expected_address) {
    const std::string mnemonic = bip39::generate_mnemonic(entropy);
    const std::string seed = bip39::mnemonic2seed(mnemonic);
    const std::string addr = hdkey::HDKeyEth::seed2addr(seed);

    std::cout << "Mnemonic:\n " << mnemonic << std::endl;
    std::cout << "\nSeed:\n " << seed << std::endl;
    std::cout << "\nAddr:\n " << addr << std::endl;
    return addr == expected_address;
}

}  // namespace bruteforce
