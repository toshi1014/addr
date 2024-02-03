cmake_minimum_required(VERSION 3.22 FATAL_ERROR)

project(attacker)

set(SRC_DIR src)
set(EXE_FILENAME a.out)
# set(CMAKE_CXX_FLAGS_DEBUG "-g")
set(OPENSSL_USE_STATIC_LIBS TRUE)

include(FetchContent)
find_package(OpenSSL REQUIRED)

add_compile_options(
    -O0
    -mtune=native
    -march=native

    -std=c++17
    -Wall
    --pedantic-error
)

FILE(GLOB CPP_FILE ${SRC_DIR}/*.cpp)

add_library(
    mylib
    STATIC
    ${CPP_FILE}
)

add_executable(
    ${EXE_FILENAME}
    ${SRC_DIR}/main.cpp
)

include_directories(include)

target_include_directories(
    ${EXE_FILENAME}
    PRIVATE
    /usr/include/openssl/
)

target_link_libraries(
    ${EXE_FILENAME}
    mylib
    OpenSSL::Crypto
    sqlite3
    /usr/local/lib/libsecp256k1.a
    /usr/local/lib/libsecp256k1.a
    ${CMAKE_CURRENT_SOURCE_DIR}/../rusthash/target/release/librusthash.a
    nlohmann_json::nlohmann_json
)

# json lib
FetchContent_Declare(
    json
    URL
    https://github.com/nlohmann/json/releases/download/v3.10.5/json.tar.xz
)
FetchContent_MakeAvailable(json)
target_link_libraries(
    mylib
    PRIVATE
    nlohmann_json::nlohmann_json
)
