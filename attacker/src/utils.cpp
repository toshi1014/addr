#include "utils.hpp"

namespace utils {

json read_json(const std::string& filepath) {
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

void time_delta(const TimePoint& time_start, const std::string& func_name) {
    auto time_end = std::chrono::high_resolution_clock::now();
    std::chrono::duration<double, std::milli> duration = time_end - time_start;
    std::cout << func_name << "\t" << duration.count() << " ms" << std::endl;
}

void set_priority(int8_t priority) {
    pid_t pid = getpid();

    if (setpriority(PRIO_PROCESS, pid, priority) == -1) {
        perror("setpriority");
        exit(1);
    }

    int new_priority = getpriority(PRIO_PROCESS, pid);
    if (new_priority == -1 && errno != 0) {
        perror("getpriority");
        exit(1);
    }
    // std::cout << "Process priority: " << new_priority << std::endl;
}

}  // namespace utils
