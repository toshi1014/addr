#ifndef DB_HPP
#define DB_HPP

#include <sqlite3.h>

#include <cstdint>
#include <functional>
#include <iostream>
#include <vector>

namespace db {

// FIXME: db dir
const std::string DB_DIR = "./db";

const std::string db_filepath = DB_DIR + "/out.db";

class DBSqlite {
   private:
    sqlite3 *db = NULL;
    static constexpr const char *optimizes[] = {
        "PRAGMA journal_mode = OFF;",    "PRAGMA synchronous = OFF;",
        "PRAGMA temp_store = MEMORY;",   "PRAGMA cache_size = -64000;",
        "PRAGMA mmap_size = 268435456;", "PRAGMA optimize;"};

    int ret = sqlite3_open(db_filepath.c_str(), &db);
    int count = 0;

    const std::string get_tbl_name(const std::string &) const;

   public:
    bool has_balance(const std::string &);
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
