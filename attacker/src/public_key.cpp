#include "public_key.hpp"

namespace public_key {

const std::string PublicKey::parse_pubkey(size_t from, int32_t to) const {
    std::stringstream point;

    for (int32_t idx = from; to <= idx; idx--) {
        point << std::setfill('0') << std::right << std::setw(2)
              << hash::dec2hex_naive((int32_t)this->pubkey.data[idx]);
    }

    return point.str();
}

PublicKey::PublicKey(const uint512_t int_seckey) {
    const std::string rhex_seckey = hash::dec2hex<uint512_t>(int_seckey);

    std::ostringstream oss;
    oss << std::setw(64) << rhex_seckey;
    const std::string hex_seckey = oss.str();

    for (size_t i = 0; i < 32; i++) {
        std::string s = hex_seckey.substr(i * 2, 2);
        uint32_t dec{0};
        if (s == "  ") {
            s = s[1];
        } else {
            if (s[0] == ' ') {
                s = s[1];
            }
            dec = hash::hex2dec<uint32_t>(s);
        }
        this->seckey[i] = dec;
    }

    this->ctx = secp256k1_context_create(SECP256K1_CONTEXT_NONE);

    int32_t return_val = secp256k1_ec_pubkey_create(ctx, &this->pubkey, seckey);
    assert(return_val);
}

const std::string PublicKey::get_x() const {
    return this->parse_pubkey(sizeof(this->pubkey) / 2 - 1,  // from
                              0                              // to
    );
};
const std::string PublicKey::get_y() const {
    return this->parse_pubkey(sizeof(this->pubkey) - 1,  // from
                              sizeof(this->pubkey) / 2   // to
    );
};

const std::string PublicKey::compressed() const {
    unsigned char compressed_pubkey[33];
    size_t len = sizeof(compressed_pubkey);
    assert(secp256k1_ec_pubkey_serialize(ctx, compressed_pubkey, &len, &pubkey,
                                         SECP256K1_EC_COMPRESSED));
    assert(len == sizeof(compressed_pubkey));

    std::stringstream ss;
    for (size_t i = 0; i < sizeof(compressed_pubkey); i++) {
        ss << std::setfill('0') << std::right << std::setw(2)
           << hash::dec2hex_naive((int32_t)compressed_pubkey[i]);
    }
    return ss.str();
}

PublicKey::~PublicKey() {
    secp256k1_context_destroy(this->ctx);
    secure_erase(this->seckey, sizeof(this->seckey));
}

};  // namespace public_key
