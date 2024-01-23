#include <fstream>
#include <nlohmann/json.hpp>

namespace utils {

using nlohmann::json;

json read_json(const std::string filepath) {
    std::ifstream f(filepath);
    json j;
    f >> j;
    return j;
}

}  // namespace utils
