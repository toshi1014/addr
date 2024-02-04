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

const double clock() {
    using namespace std::chrono;

    return (duration_cast<milliseconds>(steady_clock::now().time_since_epoch())
                .count());
}

bool line_notify(const std::string& token, const std::string& msg) {
    constexpr auto URL = "https://notify-api.line.me/api/notify";
    const std::string cmd = "curl -X POST -H 'Authorization: Bearer " + token +
                            "' -F 'message=" + msg + "' " + URL;
    return system(cmd.c_str());
}

}  // namespace utils
