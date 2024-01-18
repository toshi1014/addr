cmake_minimum_required(VERSION 3.22 FATAL_ERROR)

project(attacker)

set(SRC_DIR .)
set(EXE_FILENAME a.out)
set(CMAKE_CXX_FLAGS_DEBUG "-O0 -g")
set(OPENSSL_USE_STATIC_LIBS TRUE)

find_package(OpenSSL REQUIRED)

add_compile_options(
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

target_include_directories(
    ${EXE_FILENAME}
    PRIVATE
    /usr/include/openssl/
)

target_link_libraries(
    ${EXE_FILENAME}
    mylib
    OpenSSL::Crypto
)
