#ifndef BIP39_HPP
#define BIP39_HPP
#include <stdint.h>
#include <sys/random.h>

#include <boost/multiprecision/cpp_int.hpp>
#include <ostream>
#include <sstream>

#include "collections.hpp"

namespace bip39 {
using namespace boost::multiprecision;

const uint32_t ITER_PBKDF2_HMAC = 2048;
const uint32_t SIZE_PBKDF2_HMAC = 64;

namespace entropy {
uint128_t increment(const uint32_t);
uint128_t CSPRNG(const uint32_t);
// uint32_t PRNG(uint32_t strength);
}  // namespace entropy

std::string generate_mnemonic(const uint128_t);
collections::HexArrayPtr mnemonic2seed(const std::string&);

}  // namespace bip39
#endif
