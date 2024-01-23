#ifndef DB_HPP
#define DB_HPP

#include <sqlite3.h>

#include <iostream>
#include <vector>

namespace db {

static bool found{false};

static int callback(void *, int, char **, char **);

class DBSqlite {
   private:
    sqlite3 *db = NULL;
    int ret = sqlite3_open("./out2.db", &db);
    int count = 0;

    std::vector<std::string> eth_idx;
    std::string get_tbl_name(const std::string &);

   public:
    bool has_balance(const std::string &);
    DBSqlite();
    ~DBSqlite();
};
}  // namespace db

#endif
