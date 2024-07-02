cmake_minimum_required(VERSION 3.22 FATAL_ERROR)

project(attacker)

set(SRC_DIR src)
set(EXE_FILENAME a.out)
set(OPENSSL_USE_STATIC_LIBS TRUE)

include(FetchContent)
find_package(OpenSSL REQUIRED)
find_package(OpenMP REQUIRED)

# compile mode
set(CMAKE_CXX_FLAGS "-std=c++17 -Wall --pedantic-error")
set(CMAKE_CXX_FLAGS_DEBUG "${CMAKE_CXX_FLAGS} -pg -O0")
set(CMAKE_CXX_FLAGS_RELEASE "${CMAKE_CXX_FLAGS} -O3 -mtune=native -march=native ${OpenMP_CXX_FLAGS}")

if(CMAKE_BUILD_TYPE STREQUAL "")
    message(STATUS "Building normally")
elseif(CMAKE_BUILD_TYPE STREQUAL "Debug")
    message(STATUS "Building in Debug mode")
elseif(CMAKE_BUILD_TYPE STREQUAL "Release")
    add_definitions(-DRELEASE_MODE)
    message(STATUS "Building in Release mode")
else()
    message(FATAL_ERROR "Unknown build type: ${CMAKE_BUILD_TYPE}")
endif()


# AddressSanitizer
# set(CMAKE_C_FLAGS "${CMAKE_C_FLAGS}e -fsanitize=address -fno-omit-frame-pointer")
# set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -fsanitize=address -fno-omit-frame-pointer")
# set(CMAKE_EXE_LINKER_FLAGS "${CMAKE_EXE_LINKER_FLAGS} -fsanitize=address")
# set(CMAKE_SHARED_LINKER_FLAGS "${CMAKE_SHARED_LINKER_FLAGS} -fsanitize=address")

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
    ${CMAKE_CURRENT_SOURCE_DIR}/../rusthash/target/release/librusthash.a
    nlohmann_json::nlohmann_json
    ${OpenMP_CXX_FLAGS}
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
