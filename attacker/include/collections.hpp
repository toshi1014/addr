#ifndef COLLECTIONS_HPP
#define COLLECTIONS_HPP

#include <cassert>
#include <cstring>
#include <iomanip>
#include <iostream>
#include <memory>
#include <sstream>

namespace collections {

constexpr size_t HEX_ARRAY_SIZE{100};

class HexArray {
   private:
    unsigned char array[HEX_ARRAY_SIZE];
    unsigned char byte[HEX_ARRAY_SIZE];
    size_t size;

   public:
    explicit HexArray(unsigned char[], size_t);
    static HexArray from_str(const std::string&);
    const unsigned char* get_array() const;
    const unsigned char* get_byte() const;
    const size_t get_size() const;
    const std::string to_str() const;
    const std::string to_str_arr() const;
};

using HexArrayPtr = std::unique_ptr<HexArray>;

}  // namespace collections

#endif
