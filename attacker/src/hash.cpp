#include "hash.hpp"

namespace hash {

collections::HexArrayPtr sha256(const char* char_arr, const size_t size) {
    unsigned char hash[SHA256_DIGEST_LENGTH];
    SHA256_CTX sha256;
    SHA256_Init(&sha256);
    SHA256_Update(&sha256, char_arr, size);
    SHA256_Final(hash, &sha256);

    return collections::HexArrayPtr(
        new collections::HexArray{hash, SHA256_DIGEST_LENGTH});
}

collections::HexArrayPtr hexSha256(const collections::HexArray& hexarr) {
    return sha256((const char*)hexarr.get_byte(), hexarr.get_size() / 2);
}

const std::string hex2bin_char(const char& c) {
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

const std::string hex2bin(const std::string& hex) {
    std::stringstream ss;
    for (const char& c : hex) {
        ss << hex2bin_char(c);
    }

    return ss.str();
}

const uint32_t bin2dec(const std::string& bin) {
    uint32_t rtn = 0;

    for (uint32_t i = 0; i <= bin.length() - 1; i++) {
        rtn += ((int)(bin[i]) - '0') * std::pow(2, bin.length() - i - 1);
    }
    return rtn;
}

collections::HexArrayPtr PBKDF2_HMAC_SHA_512(const char* pass, const char* salt,
                                             const int32_t iterations,
                                             const uint32_t hash_size) {
    unsigned char* digest = new unsigned char[hash_size];

    PKCS5_PBKDF2_HMAC(pass, strlen(pass), (const unsigned char*)salt,
                      strlen(salt), iterations, EVP_sha512(), hash_size,
                      digest);

    return collections::HexArrayPtr(
        new collections::HexArray{digest, hash_size});
}

collections::HexArrayPtr hmac(const char* msg, const size_t msg_size,
                              const char* key, const size_t key_size,
                              const EVP_MD* hash_func, unsigned int hash_size) {
    unsigned char hash[100] = {};

    HMAC_CTX* hmac = HMAC_CTX_new();
    HMAC_Init_ex(hmac, key, key_size, hash_func, NULL);
    HMAC_Update(hmac, (unsigned char*)&(msg[0]), msg_size);
    HMAC_Final(hmac, hash, &hash_size);
    HMAC_CTX_free(hmac);

    return collections::HexArrayPtr(new collections::HexArray{hash, hash_size});
}

collections::HexArrayPtr hexHmac(const collections::HexArray& msg_hexarr,
                                 const std::string& key,
                                 const EVP_MD* hash_func,
                                 const unsigned int hash_size) {
    return hmac((const char*)msg_hexarr.get_array(), msg_hexarr.get_size(),
                key.c_str(), key.length(), hash_func, hash_size);
}

collections::HexArrayPtr hexHmacHexKey(const collections::HexArray& msg_hexarr,
                                       const collections::HexArray& key_hexarr,
                                       const EVP_MD* hash_func,
                                       const unsigned int hash_size) {
    return hmac((const char*)msg_hexarr.get_byte(), msg_hexarr.get_size() / 2,
                (const char*)key_hexarr.get_byte(), key_hexarr.get_size() / 2,
                hash_func, hash_size);
}

template <typename T>
const T hex2dec(const std::string& hex) {
    T out = 0;
    uint32_t size = hex.length();
    for (uint32_t i = 0; i < size; i++)
        out += static_cast<T>(std::stoi(hex2bin_char(hex[i]), NULL, 2) *
                              std::pow(16, size - i - 1));
    return out;
}
template const uint8_t hex2dec<uint8_t>(const std::string&);
template const uint32_t hex2dec<uint32_t>(const std::string&);
template const int32_t hex2dec<int32_t>(const std::string&);
template const uint128_t hex2dec<uint128_t>(const std::string&);
template const uint512_t hex2dec<uint512_t>(const std::string&);

const std::string dec2hex_naive(const uint32_t dec) {
    std::stringstream ss;
    ss << std::hex << dec;
    return ss.str();
}

template <typename T>
const std::string dec2hex(const T raw_src) {
    std::string out{""};
    T src{raw_src}, quo{src};
    uint32_t rem{0};

    while (quo > 15) {
        quo = src / 16;
        rem = (uint32_t)src % 16;
        src = quo;
        out = dec2hex_naive(rem) + out;
    }

    out = dec2hex_naive((uint32_t)quo) + out;
    return out;
}
template const std::string dec2hex<int32_t>(const int32_t);
template const std::string dec2hex<uint512_t>(const uint512_t);

const std::string hexRipemd160(const collections::HexArray& hexarr) {
    uint8_t ripeHash[RIPEMD160_DIGEST_LENGTH];
    RIPEMD160((const unsigned char*)hexarr.get_byte(), hexarr.get_size() / 2,
              ripeHash);

    std::stringstream ss1, ss2;
    for (const auto& h : ripeHash) {
        ss1 << std::setfill('0') << std::right << std::setw(2) << std::hex
            << (int)h;
    }
    ss2 << std::setfill('0') << std::right << std::setw(40) << ss1.str();
    return ss2.str();
}

const std::string sha3_256(const char* char_arr, const size_t size) {
    EVP_MD_CTX* context = EVP_MD_CTX_new();
    const EVP_MD* algo = EVP_sha3_256();

    EVP_DigestInit_ex(context, algo, nullptr);
    EVP_DigestUpdate(context, char_arr, size);

    uint32_t digest_len = EVP_MD_size(algo);
    unsigned char* digest =
        static_cast<unsigned char*>(OPENSSL_malloc(digest_len));

    EVP_DigestFinal_ex(context, digest, &digest_len);

    std::stringstream ss;
    for (uint32_t i = 0; i < digest_len; i++) {
        ss << std::hex << std::setw(2) << std::setfill('0')
           << static_cast<uint32_t>(digest[i]);
    }

    OPENSSL_free(digest);

    return ss.str();
}

// std::string hex_sha3_256(const std::string& str) {
//     char hexStr[100];
//     getHexStr(hexStr, str);
//     return sha3_256(hexStr, str.length() / 2);
// }

const uint64_t fnv1a(const collections::HexArray& hexarr) {
    const uint64_t FNV_prime = 0x100000001b3;
    const uint64_t FNV_offset_basis = 0xcbf29ce484222325;
    uint64_t hash_value = FNV_offset_basis;
    for (size_t i = 0; i < hexarr.get_size() / 2; ++i) {
        hash_value ^= hexarr.get_byte()[i];
        hash_value *= FNV_prime;
        hash_value &= 0xffffffffffffffff;  // 64-bit hash
    }
    return hash_value;
}

}  // namespace hash
