#ifndef HASH_HPP
#define HASH_HPP

#include <openssl/sha.h>

#include <iomanip>
#include <iostream>
#include <sstream>
#include <vector>

namespace hash {

std::string sha256(const char*, const uint32_t);
void getHexStr(char*, const std::string&);
std::string hexSha256(const std::string);
std::string hex2bin_char(const char&);
std::string hex2bin(const std::string&);

}  // namespace hash

#endif
