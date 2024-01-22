#include <assert.h>

#include <boost/multiprecision/cpp_int.hpp>
#include <cmath>
#include <fstream>
#include <iostream>
#include <nlohmann/json.hpp>

#include "bip39.hpp"
#include "hash.hpp"
#include "hdkey.hpp"

namespace {

using namespace boost::multiprecision;
constexpr char TEST_FILEPATH[] = "test/bip39.json";

}  // namespace

void bruteforce(const uint32_t strength) {
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

std::string entropy2addr(const std::string entropy_hex) {
    const uint128_t entropy = hash::hex2dec<uint128_t>(entropy_hex);
    const std::string mnemonic = bip39::generate_mnemonic(entropy);
    const std::string seed = bip39::mnemonic2seed(mnemonic);
    const std::string addr = hdkey::HDKey::seed2addr(seed);

    std::cout << "Entropy: " << entropy_hex << std::endl;
    std::cout << "Mnemonic: " << mnemonic << std::endl;
    std::cout << "Seed:\t" << seed << std::endl;
    std::cout << "Addr:\t" << addr << "\n" << std::endl;
    return addr;
}

void test() {
    using nlohmann::json;

    std::ifstream test_file(TEST_FILEPATH);
    json test_cases;
    test_file >> test_cases;

    for (const auto& test_case : test_cases) {
        const std::string addr_eth =
            entropy2addr(test_case["entropy"].get<std::string>());
        assert(addr_eth == test_case["eth"].get<std::string>());
    }
}

int main() {
    // bruteforce(128);

    // const std::string entropy_hex = "b0e8160f51929bf718a3f28ddc15cf27";
    // const std::string expected_addr =
    //     "0x1ca21071b051df5901614be2a085cc0d655c7c6d";
    // assert(entropy2addr(entropy_hex) == expected_addr);

    test();
}
