#ifndef ADDRESS_HPP
#define ADDRESS_HPP

#include "hdkey.hpp"

namespace address {

const std::string to_btc(const hdkey::Path, const hdkey::HDKey&);
const std::string to_eth(const hdkey::Path, const hdkey::HDKey&);

}  // namespace address

#endif
