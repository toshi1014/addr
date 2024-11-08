#ifndef DB_HPP
#define DB_HPP

#include <sqlite3.h>

#include <cstdint>
#include <functional>
#include <iostream>
#include <vector>

namespace db {

// FIXME: db
constexpr uint8_t TBL_LAST_DIGITS = 4;

const std::string DB_DIR = "./db";
const std::string db_filepath =
    DB_DIR + "/out" + std::to_string(TBL_LAST_DIGITS) + ".db";

class DBSqlite {
   private:
    sqlite3 *db = NULL;
    static constexpr const char *optimizes[] = {
        "PRAGMA journal_mode = OFF;", "PRAGMA synchronous = OFF;",
        "PRAGMA temp_store = MEMORY;",
        // "PRAGMA cache_size = -64000;",
        // "PRAGMA mmap_size = 268435456;",
        "PRAGMA optimize;"};

    int ret = 0;
    int count = 0;

    const std::string get_tbl_name(const std::string &) const;
    void check() const;

   public:
    bool has_balance(const std::string &);
    void open();
    void close();
    DBSqlite();
};

template <typename T>
void has_balance_x(DBSqlite &db_instance, const T entropy,
                   const std::string &addr,
                   std::function<void(const T aa)> callback_found) {
    if (db_instance.has_balance(addr)) callback_found(entropy);
}

const std::vector<uint8_t> fn_compress(const std::string &);

}  // namespace db

#endif
