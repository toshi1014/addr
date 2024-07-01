#include "address.hpp"

#include <openssl/ripemd.h>

#include "collections.hpp"
#include "hash.hpp"
#include "hdkey.hpp"

namespace address {

const std::string to_btc(const hdkey::Path fullpath,
                         const hdkey::HDKey& hdkey) {
    public_key::PublicKey pubkey{hdkey.get_key()};
    const std::string ripemd160ed = hash::hexRipemd160(
        *hash::hexSha256(collections::HexArray::from_str(pubkey.compressed())));

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

    const char* hashed = hash::keccak(ss_xy.str().c_str());
    const std::string addr =
        "0x" + std::string(hashed).substr(IDX_SHA3_TRIM, 100);
    delete hashed;  // free mem of rust extern
    return addr;
}

}  // namespace address
