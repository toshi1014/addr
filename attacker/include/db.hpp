#ifndef DB_HPP
#define DB_HPP

#include <sqlite3.h>

#include <iostream>
#include <vector>

namespace db {

// FIXME: db dir
const std::string DB_DIR = "./db_8k";

const std::string db_filepath = DB_DIR + "/out.db";

static bool found{false};

static int callback(void *, int, char **, char **);

class DBSqlite {
   private:
    sqlite3 *db = NULL;
    int ret = sqlite3_open(db_filepath.c_str(), &db);
    int count = 0;

    std::vector<std::string> eth_idx;
    const std::string get_tbl_name(const std::string &) const;

   public:
    bool has_balance(const std::string &);
    DBSqlite();
};
}  // namespace db

#endif
