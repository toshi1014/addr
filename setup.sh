#!/bin/bash -e

mkdir -p addr_csv db

# boost
if echo '#include <boost/version.hpp>' | g++ -E - >/dev/null 2>&1; then
    echo "Boost is already installed."
else
    echo "Installing Boost..."

    sudo apt-get update
    sudo apt-get install -y libboost-all-dev
fi

# secp256k1
if [ -f /usr/local/lib/libsecp256k1.a ]; then
    echo "libsecp256k1.a is already installed."
else
    echo "Installing libsecp256k1.a..."
    git clone git@github.com:bitcoin-core/secp256k1.git
    ./autogen.sh
    ./configure
    make
    make check
    sudo make install
fi
