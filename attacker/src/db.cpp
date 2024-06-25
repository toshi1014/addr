#include "db.hpp"

#include <fstream>
#include <nlohmann/json.hpp>

#include "collections.hpp"
#include "hash.hpp"

namespace db {

const std::string DBSqlite::get_tbl_name(const std::string &addr) const {
    size_t i = 0;
    for (const auto &a : this->eth_idx) {
        if (strcmp(addr.c_str(), a.c_str()) < 0) {
            break;
        }
        i++;
    }
    if (this->eth_idx.size() == i) i--;
    return "tbl_eth" + std::to_string(i);
}

bool DBSqlite::has_balance(const std::string &addr) {
    char *err = nullptr;
    const std::string cmd =
        "select * from " + this->get_tbl_name(addr) + " where address = ?;";

    sqlite3_stmt *stmt;
    ret = sqlite3_prepare_v2(db, cmd.c_str(), -1, &stmt, nullptr);
    if (ret != SQLITE_OK) {
        std::cerr << "SQL error: " << sqlite3_errmsg(db) << std::endl;
        sqlite3_close(db);
        exit(1);
    }

    std::vector<uint8_t> compressed = fn_compress(addr);
    ret = sqlite3_bind_blob(stmt, 1, compressed.data(), compressed.size(),
                            SQLITE_STATIC);
    while ((ret = sqlite3_step(stmt)) == SQLITE_ROW) return true;

    return false;
}

DBSqlite::DBSqlite() {
    using nlohmann::json;

    const std::string ETH_IDX_FILEPATH = DB_DIR + "/tbl_eth.json";

    std::ifstream test_file(ETH_IDX_FILEPATH);
    json test_cases;
    test_file >> test_cases;

    for (const auto &val : test_cases) {
        this->eth_idx.push_back(val.get<std::string>());
    }
}

const std::vector<uint8_t> fn_compress(const std::string &addr) {
    uint64_t hashed = hash::fnv1a(collections::HexArray::from_str(
        addr.substr(2)  // Remove the '0x' prefix
        ));

    std::vector<uint8_t> compressed(8);
    for (int i = 0; i < 8; ++i) {
        compressed[7 - i] = (hashed >> (i * 8)) & 0xFF;
    }

    return compressed;
}

}  // namespace db
