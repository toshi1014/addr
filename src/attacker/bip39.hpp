#ifndef BIP39_HPP
#define BIP39_HPP

#include <stdint.h>
#include <sys/random.h>

#include <boost/multiprecision/cpp_int.hpp>
#include <iostream>
#include <sstream>

namespace bip39 {
using namespace boost::multiprecision;

namespace entropy {
uint128_t increment(const uint32_t);
uint128_t CSPRNG(const uint32_t);
// uint32_t PRNG(uint32_t strength);
}  // namespace entropy

std::string generate_mnemonic(const uint128_t);
std::string mnemonic2seed(const std::string&);

}  // namespace bip39
#endif
