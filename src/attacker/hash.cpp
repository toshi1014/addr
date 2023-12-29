#include "hash.hpp"

namespace hash {

std::string sha256(const char* charArr, const uint32_t size) {
    unsigned char hash[SHA256_DIGEST_LENGTH];
    SHA256_CTX sha256;
    SHA256_Init(&sha256);
    SHA256_Update(&sha256, charArr, size);
    SHA256_Final(hash, &sha256);

    std::stringstream ss;

    for (uint32_t i = 0; i < SHA256_DIGEST_LENGTH; i++) {
        ss << std::hex << std::setw(2) << std::setfill('0')
           << static_cast<uint32_t>(hash[i]);
    }
    return ss.str();
}

void getHexStr(char* hexStr, const std::string& str) {
    for (uint32_t i = 0; i < str.length() / 2; i++) {
        hexStr[i] = std::stol(str.substr(i * 2, 2), NULL, 16);
    }
}

std::string hexSha256(const std::string str) {
    char hexStr[100];
    getHexStr(hexStr, str);
    return sha256(hexStr, str.length() / 2);
}

}  // namespace hash
