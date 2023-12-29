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

std::string hex2bin_char(const char& c) {
    switch (c) {
        case '0':
            return "0000";
        case '1':
            return "0001";
        case '2':
            return "0010";
        case '3':
            return "0011";
        case '4':
            return "0100";
        case '5':
            return "0101";
        case '6':
            return "0110";
        case '7':
            return "0111";
        case '8':
            return "1000";
        case '9':
            return "1001";
        case 'A':
        case 'a':
            return "1010";
        case 'B':
        case 'b':
            return "1011";
        case 'C':
        case 'c':
            return "1100";
        case 'D':
        case 'd':
            return "1101";
        case 'E':
        case 'e':
            return "1110";
        case 'F':
        case 'f':
            return "1111";
        default:
            return "-1";
    }
}

std::string hex2bin(const std::string& hex) {
    std::stringstream ss;
    for (const char& c : hex) {
        ss << hex2bin_char(c);
    }

    return ss.str();
}

}  // namespace hash
