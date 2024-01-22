#ifndef HASH_HPP
#define HASH_HPP

#include <openssl/hmac.h>
#include <openssl/ripemd.h>
#include <openssl/sha.h>

#include <boost/multiprecision/cpp_int.hpp>
#include <cmath>
#include <cstring>
#include <iomanip>
#include <iostream>
#include <ostream>
#include <sstream>
#include <vector>

namespace hash {

extern "C" {
const char* keccak(const char*);
}

#pragma comment(lib, "rusthash.a.lib")

using namespace boost::multiprecision;

template <typename... Args>
std::string format(const std::string& fmt, Args... args) {
    size_t len = std::snprintf(nullptr, 0, fmt.c_str(), args...);
    std::vector<char> buf(len + 1);
    std::snprintf(&buf[0], len + 1, fmt.c_str(), args...);
    return std::string(&buf[0], &buf[0] + len);
}

void getHexStr(char*, const std::string&);
std::string sha256(const char*, const size_t);
std::string hexSha256(const std::string&);
std::string hex2bin_char(const char&);
std::string hex2bin(const std::string&);
uint32_t bin2dec(const std::string&);
std::string PBKDF2_HMAC_SHA_512(const char*, const char*, const int32_t,
                                const uint32_t);
std::string hmac(const char*, const size_t, const char*, const size_t,
                 const EVP_MD*, const unsigned int);
std::string hexHmac(const std::string&, const std::string&, const EVP_MD*,
                    const unsigned int);
std::string hexHmacHexKey(const std::string&, const std::string&, const EVP_MD*,
                          const unsigned int);
template <typename T>
T hex2dec(const std::string&);
template <typename T>
std::string dec2hex(const T);
inline std::string dec2hex_naive(const uint32_t);
std::string hexRipemd160(const std::string&);
std::string sha3_256(const char*, const size_t);
std::string hex_sha3_256(const std::string&);

}  // namespace hash

#endif
