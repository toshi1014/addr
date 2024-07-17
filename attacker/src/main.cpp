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

// param
const uint128_t INITIAL_ENTROPY{"800000000000000000000000000000000000000"};
#ifdef RELEASE_MODE
#define INTERVAL 100000
#define LIM 1000000000  // 340282366920938463463374607431768211455
#else
#define INTERVAL 1000
#define LIM 10000
#endif
const bool VERBOSE_BRUTEFORCE = false;

uint128_t (*func_gen_entropy)(uint128_t);
// end param

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
    std::cout << "\n" << entropy << ": " << mnemonic << std::endl;

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

    db::DBSqlite db{};

    std::cout << "Time\tStatus\t\titer/sec\tMem(KB)\t\tEntropy" << std::endl;
    double start_time = omp_get_wtime();
    size_t ping_cnt{0};
    constexpr uint32_t interval{INTERVAL};
    std::map<uint128_t, std::string> addr_pool;
    uint128_t entropy = INITIAL_ENTROPY;

#ifdef RELEASE_MODE
    utils::set_priority(-20);
    omp_set_num_threads(omp_get_max_threads());
#pragma omp parallel for schedule(dynamic, 1)
#endif
    for (size_t i = 0; i <= LIM; i++) {
        entropy = func_gen_entropy(entropy);
        const std::string addr = entropy2addr(entropy, VERBOSE_BRUTEFORCE);

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

void show_time_delta() {
    db::DBSqlite db{};

    utils::TimePoint time_start = std::chrono::high_resolution_clock::now();

    const uint128_t entropy =
        utils::deco_time_delta(func_gen_entropy, "func_gen_entropy")(entropy);
    const std::string mnemonic = utils::deco_time_delta(
        bip39::generate_mnemonic, "generate_mnemonic")(entropy);

    const collections::HexArrayPtr seed_hexarr = utils::deco_time_delta(
        bip39::mnemonic2seed, "mnemonic2seed\t")(mnemonic);

    const std::string addr = utils::deco_time_delta(
        hdkey::HDKey::seed2addr, "seed2addr\t")(*seed_hexarr);

    for (size_t i = 0; i < 1; i++) {
        time_start = std::chrono::high_resolution_clock::now();
        if (db.has_balance(addr)) found(entropy);
        utils::time_delta(time_start, "has_balance\t");
    }

    std::cout << "\n\nMnemonic:\t" << mnemonic << std::endl;
    std::cout << "Seed:\t" << seed_hexarr->to_str() << std::endl;
    std::cout << "Addr:\t" << addr << "\n" << std::endl;
}

}  // namespace

int main() {
    // show info
    std::stringstream ss;
#ifdef RELEASE_MODE
    ss << "[RELEASE_MODE]\n";
#endif
    ss << "Entropy: ";
#ifdef ENTROPY_RANDOM
    ss << "random\n";
#elif defined(ENTROPY_INCREMENT)
    ss << "increment (from " << INITIAL_ENTROPY << ")\n";
#else
    std::cerr << "Bad entropy type" << std::endl;
    exit(1);
#endif
    ss << "Limit:\t " << LIM << "\n";

    std::cout << ss.str() << std::endl;
    // end show info

    func_gen_entropy =
#ifdef ENTROPY_RANDOM
        *bip39::entropy::CSPRNG;
#elif defined(ENTROPY_INCREMENT)
        *bip39::entropy::increment;
#else
        NULL;
#endif

    bruteforce(128);
    // test();
    // show_time_delta();

    // const std::string entropy_hex = "b0e8160f51929bf718a3f28ddc15cf27";
    // const std::string expected_addr =
    //     "0x1ca21071b051df5901614be2a085cc0d655c7c6d";
    // assert(entropy2addr(entropy_hex, /*verbose*/ true) == expected_addr);
}
