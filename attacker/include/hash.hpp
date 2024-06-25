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

#include "collections.hpp"

namespace hash {

extern "C" {
const char* keccak(const char*);
}

#pragma comment(lib, "rusthash.a.lib")

using namespace boost::multiprecision;

template <typename... Args>
const std::string format(const std::string& fmt, Args... args) {
    size_t len = std::snprintf(nullptr, 0, fmt.c_str(), args...);
    std::vector<char> buf(len + 1);
    std::snprintf(&buf[0], len + 1, fmt.c_str(), args...);
    return std::string(&buf[0], &buf[0] + len);
}

collections::HexArrayPtr sha256(const char* char_arr, const size_t size);
collections::HexArrayPtr hexSha256(const collections::HexArray&);

const std::string hex2bin_char(const char&);
const std::string hex2bin(const std::string&);
const uint32_t bin2dec(const std::string&);

collections::HexArrayPtr PBKDF2_HMAC_SHA_512(const char*, const char*,
                                             const int32_t, const uint32_t);

collections::HexArrayPtr hmac(const char*, const size_t, const char*,
                              const size_t, const EVP_MD*, const unsigned int);
collections::HexArrayPtr hexHmac(const collections::HexArray&,
                                 const std::string&, const EVP_MD*,
                                 const unsigned int);
collections::HexArrayPtr hexHmacHexKey(const collections::HexArray&,
                                       const collections::HexArray&,
                                       const EVP_MD*, const unsigned int);
template <typename T>
const T hex2dec(const std::string&);

template <typename T>
const std::string dec2hex(const T);

const std::string dec2hex_naive(const uint32_t);

const std::string hexRipemd160(const collections::HexArray&);
const std::string sha3_256(const char*, const size_t);
const std::string hex_sha3_256(const std::string&);

const uint64_t fnv1a(const collections::HexArray&);

}  // namespace hash

#endif
