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

enum Network { BtcLegacy, BtcSegwit, Eth };

enum Encoding { base58, bech32 };

const uint512_t CURVE_N(
    "11579208923731619542357098500868790785283756427907490438260516314151816149"
    "4337");

using Path = std::vector<std::string>;

class HDKey {
   private:
    uint512_t key;
    std::string chain_code;
    uint32_t depth;
    Encoding encoding;
    std::string prefix;

   public:
    HDKey(uint512_t, std::string, uint32_t, Encoding, std::string);
    static HDKey from_seed(const std::string&, const Encoding&,
                           const std::string&);
    static HDKey child_private(HDKey&, uint32_t, bool);
    static HDKey subkey(HDKey&, std::string);
    static std::string seed2addr(const std::string&);
};

}  // namespace hdkey

#endif