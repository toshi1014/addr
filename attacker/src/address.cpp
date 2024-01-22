#include "address.hpp"

#include <openssl/ripemd.h>

#include "hash.hpp"
#include "hdkey.hpp"

namespace address {

const std::string to_btc(const hdkey::Path fullpath,
                         const hdkey::HDKey& hdkey) {
    public_key::PublicKey pubkey{hdkey.get_key()};
    const std::string hex_hash = hash::hexSha256(pubkey.compressed());
    const std::string ripemd160ed = hash::hexRipemd160(hex_hash);

    return "A";
}

const std::string to_eth(const hdkey::Path fullpath,
                         const hdkey::HDKey& hdkey) {
    constexpr size_t SIZE = 32;
    constexpr size_t IDX_SHA3_TRIM = 24;

    public_key::PublicKey pubkey{hdkey.get_key()};
    std::stringstream ss_xy;
    ss_xy << std::setfill('0') << std::right << std::setw(SIZE)
          << pubkey.get_x()  // x
          << std::setfill('0') << std::right << std::setw(SIZE)
          << pubkey.get_y();  // y

    const std::string hashed = hash::keccak(ss_xy.str().c_str());
    return "0x" + hashed.substr(IDX_SHA3_TRIM, 100);
}

}  // namespace address
