#ifndef PUBLIC_KEY_HPP
#define PUBLIC_KEY_HPP

#include <secp256k1.h>

#include "hash.hpp"

namespace public_key {

using namespace boost::multiprecision;

class PublicKey {
   private:
    secp256k1_context* ctx;
    unsigned char seckey[32];

    std::string parse_pubkey(size_t, int32_t);

   public:
    secp256k1_pubkey pubkey;

    PublicKey(const uint512_t);
    std::string get_x();
    std::string get_y();
    std::string compressed();
    ~PublicKey();
};

/* Cleanses memory to prevent leaking sensitive info. Won't be optimized out. */
static void secure_erase(void* ptr, size_t len) {
    /* We use a memory barrier that scares the compiler away from optimizing out
     * the memset.
     *
     * Quoting Adam Langley <agl@google.com> in commit
     * ad1907fe73334d6c696c8539646c21b11178f20f in BoringSSL (ISC License): As
     * best as we can tell, this is sufficient to break any optimisations that
     *    might try to eliminate "superfluous" memsets.
     * This method used in memzero_explicit() the Linux kernel, too. Its
     * advantage is that it is pretty efficient, because the compiler can still
     * implement the memset() efficiently, just not remove it entirely. See
     * "Dead Store Elimination (Still) Considered Harmful" by Yang et al.
     * (USENIX Security 2017) for more background.
     */
    memset(ptr, 0, len);
    __asm__ __volatile__("" : : "r"(ptr) : "memory");
}

}  // namespace public_key

#endif
