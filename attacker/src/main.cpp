#include <omp.h>

#include <boost/multiprecision/cpp_int.hpp>
#include <cassert>
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
    std::cout << mnemonic << std::endl;

    // file write
    std::ofstream file;
    file.open("found.txt", std::ios::app);
    file << mnemonic << "\n";
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
    // const std::string strLim = "340282366920938463463374607431768211455";
    constexpr uint32_t interval{9000};
    const std::string strLim = "100000000";

    // const uint128_t lim{strLim};
    const uint32_t lim{static_cast<uint32_t>(stoi(strLim))};

    db::DBSqlite db{};
    uint128_t (*func_gen_entropy)(uint32_t);
    func_gen_entropy = *bip39::entropy::CSPRNG;

    std::cout << "Time\tStatus\t\titer/sec" << std::endl;
    double start_time = omp_get_wtime();
    size_t ping_cnt{0};
    std::map<uint128_t, std::string> addr_pool;

    // #pragma omp parallel
    {
        // #pragma omp for
        for (uint32_t i = 0; i <= lim; i++) {
            const uint128_t entropy = func_gen_entropy(i);
            const std::string addr = entropy2addr(entropy, /*verbose=*/false);

            if (db.has_balance(addr)) found(entropy);
            // addr_pool.insert({entropy, addr});

            // once in a while,
            if (i % interval == 0) {
                utils::show_status(start_time, "searching...", NULL);

                std::vector<std::thread> threads;

                // 1. has_balance
                for (const auto& pair : addr_pool)
                    threads.emplace_back(db::has_balance_x<uint128_t>,
                                         std::ref(db),
                                         /*entropy=*/pair.first,
                                         /*addr=*/pair.second,
                                         /*callback_found=*/found);
                for (auto& thread : threads) thread.join();
                addr_pool.clear();

                // 2. ping
                ping(db);

                // 3. show iter/sec
                utils::show_status(start_time, "interval", interval * ping_cnt);
                ping_cnt++;
            }
        }
    }

    utils::show_status(start_time, "finish\t", interval * ping_cnt);
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
