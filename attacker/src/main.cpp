#include <omp.h>

#include <boost/multiprecision/cpp_int.hpp>
#include <cassert>
#include <chrono>
#include <cmath>
#include <fstream>
#include <iostream>
#include <map>
#include <thread>

#include "bip39.hpp"
#include "collections.hpp"
#include "db.hpp"
#include "hash.hpp"
#include "hdkey.hpp"
#include "utils.hpp"

// param
constexpr uint8_t INITIAL_ENTROPY = 7;
#ifdef RELEASE_MODE
#define INTERVAL 1000000
#define LIM 1000000000  // 340282366920938463463374607431768211455
#else
#define INTERVAL 1000
#define LIM 10000
#endif
// end param

namespace {

using namespace boost::multiprecision;
using nlohmann::json;
constexpr char TEST_FILEPATH[] = "test/bip39.json";
constexpr char CONFIG_FILEPATH[] = "config.json";

const auto config = utils::read_json(CONFIG_FILEPATH);

const std::string entropy2addr(const uint128_t entropy, bool verbose) {
    const std::string mnemonic = bip39::generate_mnemonic(entropy);
    const collections::HexArrayPtr seed_hexarr = bip39::mnemonic2seed(mnemonic);
    const std::string addr = hdkey::HDKey::seed2addr(*seed_hexarr);

    if (verbose) {
        std::cout << "Mnemonic:\t" << mnemonic << std::endl;
        std::cout << "Seed:\t" << seed_hexarr->to_str() << std::endl;
        std::cout << "Addr:\t" << addr << "\n" << std::endl;
    }
    return addr;
}

const std::string entropy2addr(const std::string entropy_hex, bool verbose) {
    if (verbose) std::cout << "Entropy:\t" << entropy_hex << std::endl;

    const uint128_t entropy = hash::hex2dec<uint128_t>(entropy_hex);
    return entropy2addr(entropy, verbose);
}

void found(const uint128_t entropy) {
    const std::string mnemonic = bip39::generate_mnemonic(entropy);
    std::cout << entropy << ": " << mnemonic << std::endl;

    // file write
    std::ofstream file;
    file.open("found.txt", std::ios::app);
    file << entropy << ": " << mnemonic << "\n";
    file.close();

    utils::line_notify(/*token=*/config["LINE_TOKEN"], /*msg=*/mnemonic);
}

void ping(db::DBSqlite db) {
    for (const std::string& entropy_hex : config["PING_DATA"]["entropy"]) {
        assert(db.has_balance(entropy2addr(entropy_hex, /*verbose*/ false)));
    }
}

void bruteforce(const uint32_t strength) {
    assert(strength == 128 || strength == 256);

    uint128_t (*func_gen_entropy)(uint128_t);
    // func_gen_entropy = *bip39::entropy::CSPRNG;
    func_gen_entropy = *bip39::entropy::increment;

    db::DBSqlite db{};
    db.open();

    std::cout << "Time\tStatus\t\titer/sec\tMem(KB)\t\tEntropy" << std::endl;
    double start_time = omp_get_wtime();
    size_t ping_cnt{0};
    constexpr uint32_t interval{INTERVAL};
    const __uint128_t lim{LIM};
    std::map<uint128_t, std::string> addr_pool;

#ifdef RELEASE_MODE
#pragma omp parallel
#endif
    {
#ifdef RELEASE_MODE
#pragma omp for
#endif
        for (__uint128_t i = INITIAL_ENTROPY; i <= lim; i++) {
            const uint128_t entropy = func_gen_entropy(i);
            const std::string addr = entropy2addr(entropy, /*verbose=*/false);

            if (db.has_balance(addr)) found(entropy);
            // addr_pool.insert({entropy, addr});

            // once in a while,
            if (i % interval == 0) {
                // 1. has_balance
                if (!addr_pool.empty()) {
                    utils::show_status(start_time, "searching...", NULL, NULL);

                    std::vector<std::thread> threads;

                    for (const auto& pair : addr_pool)
                        threads.emplace_back(db::has_balance_x<uint128_t>,
                                             std::ref(db),
                                             /*entropy=*/pair.first,
                                             /*addr=*/pair.second,
                                             /*callback_found=*/found);
                    for (auto& thread : threads) thread.join();
                    addr_pool.clear();
                }

                // 2. ping
                ping(db);

                // 3. show iter/sec
                utils::show_status(start_time, "interval", interval * ping_cnt,
                                   entropy.str());
                ping_cnt++;
            }
        }
    }

    utils::show_status(start_time, "finish\t", interval * (ping_cnt - 1),
                       std::to_string(LIM));
}

void test() {
    const auto test_cases = utils::read_json(TEST_FILEPATH);

    for (const auto& test_case : test_cases) {
        const std::string addr_eth = entropy2addr(
            test_case["entropy"].get<std::string>(), /*verbose=*/true);
        assert(addr_eth == test_case["eth"].get<std::string>());
    }
}

}  // namespace

int main() {
    bruteforce(128);

    // const std::string entropy_hex = "b0e8160f51929bf718a3f28ddc15cf27";
    // const std::string expected_addr =
    //     "0x1ca21071b051df5901614be2a085cc0d655c7c6d";
    // assert(entropy2addr(entropy_hex, /*verbose*/ true) == expected_addr);

    // test();
}
