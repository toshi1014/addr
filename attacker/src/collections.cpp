#include <collections.hpp>

#include "hash.hpp"

namespace collections {

HexArray::HexArray(unsigned char arr[], size_t arr_size) {
    assert(arr_size > 0 && arr_size < HEX_ARRAY_SIZE);
    this->size = arr_size;
    std::memcpy(&array, arr, arr_size);

    for (uint32_t i = 0; i < this->size; i += 2) {
        this->byte[i / 2] = this->array[i] * 16 + this->array[i + 1];
    }
}

HexArray HexArray::from_str(const std::string& str) {
    unsigned char array[HEX_ARRAY_SIZE];
    size_t idx{0};
    uint32_t dec;

    for (const auto& c : str) {
        if (c >= 'a' && c <= 'f') {
            dec = (uint32_t)c - 87;
        } else if (c >= '0' && c <= '9') {
            dec = (uint32_t)c - 48;
        } else {
            std::cerr << "Bad hex str in HexArray" << std::endl;
            exit(1);
        }

        array[idx] = dec;
        idx++;
    }

    return HexArray{array, idx};
}

const unsigned char* HexArray::get_array() const { return this->array; }
const unsigned char* HexArray::get_byte() const { return this->byte; }
const size_t HexArray::get_size() const { return this->size; }

const std::string HexArray::to_str() const {
    std::stringstream ss;
    for (size_t i = 0; i < this->size; i++) {
        ss << hash::format("%02x", this->array[i]);
    }
    return ss.str();
}

const std::string HexArray::to_str_arr() const {
    std::stringstream ss;
    ss << "{";
    for (size_t i = 0; i < this->size; i++) {
        ss << std::to_string((uint32_t)this->array[i]) << ", ";
    }
    ss << "}";
    return ss.str();
}

}  // namespace collections
