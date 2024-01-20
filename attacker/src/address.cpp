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
    constexpr uint32_t SIZE = 32;
    public_key::PublicKey pubkey{hdkey.get_key()};
    std::stringstream ss;
    ss << std::setfill('0') << std::right << std::setw(SIZE)
       << pubkey.get_x()  // x
       << std::setfill('0') << std::right << std::setw(SIZE)
       << pubkey.get_y();  // y

    std::string output = hash::hex_sha3_256(ss.str());
    std::cout << ss.str() << std::endl;
    std::cout << output << std::endl;

    return "A";
}

}  // namespace address
