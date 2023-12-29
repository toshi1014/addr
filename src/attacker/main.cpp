#include <boost/multiprecision/cpp_int.hpp>

#include "bruteforce.hpp"
using namespace boost::multiprecision;

int main() {
    // bruteforce::run(128);
    assert(bruteforce::test(
        static_cast<uint128_t>("238628274862056977938458547489363595269"),
        "receive country neck hammer emerge walnut sadness toward bulb praise "
        "lottery anxiety"));
}
