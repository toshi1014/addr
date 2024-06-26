#include "db.hpp"

#include <fstream>

#include "collections.hpp"
#include "hash.hpp"

namespace db {

const std::string DBSqlite::get_tbl_name(const std::string &addr) const {
    return "tbl_eth" +
           std::to_string(hash::hex2dec<uint8_t>(addr.substr(addr.size() - 1)));
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
    // optimize
    for (auto &opt : optimizes) {
        ret = sqlite3_exec(db, opt, 0, 0, nullptr);
        if (ret != SQLITE_OK) {
            std::cerr << "SQL error during optimization" << std::endl;
            break;
        }
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
