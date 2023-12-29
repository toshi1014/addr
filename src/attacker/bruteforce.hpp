#ifndef BRUTEFORCE_HPP
#define BRUTEFORCE_HPP

#include <stdint.h>
#include <boost/multiprecision/cpp_int.hpp>

namespace bruteforce {
using namespace boost::multiprecision;

void run(const uint32_t);
bool test(const uint128_t, const std::string);

}  // namespace bruteforce

#endif
