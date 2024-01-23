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

double clock() {
    using namespace std::chrono;

    return (duration_cast<milliseconds>(steady_clock::now().time_since_epoch())
                .count());
}

}  // namespace utils
