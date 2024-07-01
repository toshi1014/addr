#include "db.hpp"

#include <fstream>

#include "collections.hpp"
#include "hash.hpp"

namespace db {

const std::string DBSqlite::get_tbl_name(const std::string &addr) const {
    return "tbl_eth" + std::to_string(hash::hex2dec<uint32_t>(
                           addr.substr(addr.size() - TBL_LAST_DIGITS)));
}

void DBSqlite::check() const {
    if (ret != SQLITE_OK) {
        std::cerr << "SQL error: " << sqlite3_errmsg(db) << std::endl;
        sqlite3_close(db);
        exit(1);
    }
}

void DBSqlite::open() {
    ret = sqlite3_open(db_filepath.c_str(), &db);
    check();
}

void DBSqlite::close() { sqlite3_close(db); }

bool DBSqlite::has_balance(const std::string &addr) {
    bool found = false;
    char *err = nullptr;
    sqlite3_stmt *stmt;

    const std::string cmd =
        "select * from " + this->get_tbl_name(addr) + " where address = ?;";

    ret = sqlite3_prepare_v2(db, cmd.c_str(), -1, &stmt, nullptr);
    check();

    const std::vector<uint8_t> compressed = fn_compress(addr);

    // NOTE: mem leak
    ret = sqlite3_bind_blob(stmt, 1, compressed.data(), compressed.size(),
                            SQLITE_TRANSIENT);
    check();

    while ((ret = sqlite3_step(stmt)) == SQLITE_ROW) found = true;
    sqlite3_finalize(stmt);

    return found;
}

DBSqlite::DBSqlite() {
    this->open();

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
