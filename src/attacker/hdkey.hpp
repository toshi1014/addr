#ifndef HDKEY_HPP
#define HDKEY_HPP

#include <boost/multiprecision/cpp_int.hpp>
#include <iostream>
#include <string>
#include <variant>
#include <vector>

#include "hash.hpp"

namespace hdkey {

using namespace boost::multiprecision;

const uint256_t CURVE_N(
    "11579208923731619542357098500868790785283756427907490438260516314151816149"
    "4337");

struct Wallet {
    std::string coin;
    std::string seed;
    std::vector<std::string> children;
    std::string xpublic_key;
    std::string addr;
};

using Path = std::vector<std::string>;

class EccPoint {
   private:
    std::string key;

   public:
    EccPoint(const std::string);
    static uint32_t get_public_key;
    std::string to_hex;
};

class PublicKey {
   private:
    const std::string MAINNET_VERSION = "0x00";

   public:
    PublicKey(const uint32_t, const uint32_t);
    std::string address(bool, bool);
    std::string to_hex();
    static std::string from_bytes();
    static std::string from_point();
    static std::string get_compressed_bytes();
};

class HDKey {
   protected:
    uint256_t key;
    std::string chain_code;
    uint32_t index;
    uint32_t depth;
    std::string parent_fingerprint;

   public:
    HDKey(uint256_t, std::string, uint32_t, uint32_t, std::string);
    std::string to_bytes();
    static std::string from_bytes();
};

class HDPrivateKey;  // previous declaration

class HDPublicKey : protected HDKey {
   private:
    const std::string MAINNET_VERSION = "0x0488B21E";

   public:
    HDPublicKey(uint256_t, std::string, uint32_t, uint32_t, std::string);
    std::string address(bool, bool);
    static HDPublicKey from_parent(HDPublicKey, const uint32_t);
    static std::string get_compressed_bytes();
};

class HDPrivateKey : protected HDKey {
   private:
   public:
    HDPrivateKey(uint256_t, std::string, uint32_t, uint32_t, std::string);
    static HDPrivateKey master_key_from_seed(const std::string&);
    static HDPrivateKey from_parent(HDPrivateKey, const uint32_t);
    static HDPublicKey public_key();
};

class HDKeyEth {
   public:
    template <typename T>
    static T from_path(T, Path);
    static HDPrivateKey create_address(const std::string&, const uint32_t,
                                       const uint32_t);
    static std::string seed2addr(const std::string&);
};

}  // namespace hdkey

#endif
