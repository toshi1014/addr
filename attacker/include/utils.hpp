#ifndef UTILS_HPP
#define UTILS_HPP

#include <omp.h>
#include <sys/resource.h>
#include <unistd.h>

#include <chrono>
#include <fstream>
#include <iostream>
#include <nlohmann/json.hpp>

namespace utils {

using nlohmann::json;
using TimePoint = std::chrono::time_point<std::chrono::high_resolution_clock>;

json read_json(const std::string&);

const double clock();

bool line_notify(const std::string&, const std::string&);
size_t getMemoryUsage();

void show_status(double, const std::string&, const uint32_t,
                 const std::string&);

void time_delta(const TimePoint&, const std::string&);

template <typename Func>
auto deco_time_delta(Func func, const std::string& func_name) {
    return [func, func_name](auto&&... args) {
        std::cout << func_name << std::flush;
        const TimePoint time_start = std::chrono::high_resolution_clock::now();
        auto result = func(std::forward<decltype(args)>(args)...);
        time_delta(time_start, "");
        return result;
    };
}

void set_priority(int8_t);

}  // namespace utils

#endif
