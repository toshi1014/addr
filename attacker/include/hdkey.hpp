#ifndef HDKEY_HPP
#define HDKEY_HPP

#include <boost/multiprecision/cpp_int.hpp>
#include <iostream>
#include <optional>
#include <string>
#include <variant>
#include <vector>

#include "collections.hpp"
#include "hash.hpp"
#include "public_key.hpp"

namespace hdkey {

using namespace boost::multiprecision;
using Path = std::vector<std::string>;

enum Network { BtcLegacy, BtcSegwit, Eth };
enum Encoding { base58, bech32 };
constexpr size_t KEY_SIZE = 64;

const uint512_t CURVE_N(
    "11579208923731619542357098500868790785283756427907490438260516314151816149"
    "4337");

class HDKey {
   private:
    uint512_t key;
    collections::HexArray chain_code;
    uint32_t depth;
    Encoding encoding;
    std::string prefix;

   public:
    HDKey(const uint512_t, collections::HexArray, const uint32_t,
          const Encoding, const std::string&);
    const std::string get_key_hex() const;

    static HDKey from_seed(const collections::HexArray&, const Encoding&,
                           const std::string&);
    static HDKey child_private(HDKey&, uint32_t, bool);
    static HDKey subkey(HDKey&, std::string);
    static std::string seed2addr(const collections::HexArray&);

    // COMBAK:
    const uint512_t get_key() const { return key; }
};

}  // namespace hdkey

#endif
