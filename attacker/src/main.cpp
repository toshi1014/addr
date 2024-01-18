#include <boost/multiprecision/cpp_int.hpp>

#include "bruteforce.hpp"
using namespace boost::multiprecision;

int main() {
    // bruteforce::run(128);
    assert(bruteforce::test(
        static_cast<uint128_t>("150974943580811493896868640541295935281"),
        "0x01a41a60977de7bde9d181508f3ecece41e31e55"));
}
