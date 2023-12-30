#ifndef HASH_HPP
#define HASH_HPP

#include <openssl/bio.h>
#include <openssl/evp.h>
#include <openssl/rand.h>
#include <openssl/sha.h>

#include <cstring>
#include <iomanip>
#include <iostream>
#include <sstream>
#include <vector>

namespace hash {

const uint32_t ITER_PBKDF2_HMAC= 2048;
const uint32_t SIZE_PBKDF2_HMAC= 64;

template <typename... Args>
std::string format(const std::string& fmt, Args... args) {
    size_t len = std::snprintf(nullptr, 0, fmt.c_str(), args...);
    std::vector<char> buf(len + 1);
    std::snprintf(&buf[0], len + 1, fmt.c_str(), args...);
    return std::string(&buf[0], &buf[0] + len);
}

std::string sha256(const char*, const uint32_t);
void getHexStr(char*, const std::string&);
std::string hexSha256(const std::string);
std::string hex2bin_char(const char&);
std::string hex2bin(const std::string&);
uint32_t bin2dec(const std::string&);
std::string PBKDF2_HMAC_SHA_512(const char*, const char*, const int32_t,
                                const uint32_t);

}  // namespace hash

#endif
