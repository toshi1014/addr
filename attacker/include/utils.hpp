#include <sys/resource.h>

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

size_t getMemoryUsage() {
    struct rusage usage;
    getrusage(RUSAGE_SELF, &usage);
    return usage.ru_maxrss;
}

void show_status(double start_time, const std::string& status,
                 const uint32_t num, const std::string& entropy) {
    double delta = omp_get_wtime() - start_time;
    std::cout << (uint32_t)delta << "\t" << status << "\t"
              << std::to_string(num / delta) << "\t" << getMemoryUsage()
              << "\t\t" << entropy << std::endl;
}

}  // namespace utils
