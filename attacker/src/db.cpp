#include "db.hpp"

#include <fstream>
#include <nlohmann/json.hpp>

namespace db {

static int callback(void *_, int argc, char **argv, char **columnName) {
    db::found = argc == 1;
    return SQLITE_OK;
}

const std::string DBSqlite::get_tbl_name(const std::string &addr) const {
    size_t i = 0;
    for (const auto &a : this->eth_idx) {
        if (strcmp(addr.c_str(), a.c_str()) < 0) {
            break;
        }
        i++;
    }
    return "tbl_eth" + std::to_string(i);
}

bool DBSqlite::has_balance(const std::string &addr) {
    char *err = nullptr;
    const std::string cmd = "select * from " + this->get_tbl_name(addr) +
                            " where address = '" + addr + "';";
    ret = sqlite3_exec(db, cmd.c_str(), callback, nullptr, &err);

    if (ret != SQLITE_OK) {
        if (err != nullptr) {
            std::cerr << "[ERR]\t" << err << std::endl;
            std::cerr << "[CMD]\t" << cmd << std::endl;
            exit(1);
        }
    }

    bool found_copied = db::found;
    db::found = false;
    return found_copied;
}

DBSqlite::DBSqlite() {
    using nlohmann::json;

    const std::string ETH_IDX_FILEPATH = "table_index/tbl_eth.json.tmp";

    std::ifstream test_file(ETH_IDX_FILEPATH);
    json test_cases;
    test_file >> test_cases;

    for (const auto &val : test_cases) {
        this->eth_idx.push_back(val.get<std::string>());
    }
}

}  // namespace db
