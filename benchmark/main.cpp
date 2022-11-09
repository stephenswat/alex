#include <chrono>
#include <cstdlib>
#include <iostream>

#include "matrix.hpp"


#define S 100000000

#define _N 3

#ifndef TRIALS
#define TRIALS 1
#endif

static constexpr std::size_t N = _N;

int main() {
    char * q = reinterpret_cast<char *>(malloc(S));

    std::chrono::high_resolution_clock::time_point t1 = std::chrono::high_resolution_clock::now();

    for (int t = 0; t < TRIALS; ++t) {
        for (int  i = 0; i < S; ++i) {
            q[i] = i % 32;
        }
    }

    std::chrono::high_resolution_clock::time_point t2 = std::chrono::high_resolution_clock::now();

    std::cout << ((static_cast<double>(TRIALS) * static_cast<double>(S)) / std::chrono::duration_cast<std::chrono::nanoseconds>(t2 - t1).count()) << std::endl;

    return 0;
}
