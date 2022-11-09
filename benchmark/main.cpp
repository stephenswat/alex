#include <chrono>
#include <cstdlib>
#include <iostream>

#include "matrix.hpp"

#ifndef TRIALS
#define TRIALS 10
#endif

using matrix_t = matrix<std::index_sequence<PERMUTATION>>;

int main() {
    std::size_t s = 0;

    for (int t = 0; t < TRIALS; ++t) {
        matrix_t a = matrix_t::random();
        matrix_t b = matrix_t::random();
        matrix_t c;

        std::chrono::high_resolution_clock::time_point t1 = std::chrono::high_resolution_clock::now();

        for (std::size_t i = 0; i < matrix_t::N; ++i) {
            for (std::size_t j = 0; j < matrix_t::M; ++j) {
                float acc = 0.f;

                for (std::size_t k = 0; k < matrix_t::N; ++k) {
                    acc += a(i, k) * b(k, j);
                }

                c(i, j) = acc;
            }
        }

        std::chrono::high_resolution_clock::time_point t2 = std::chrono::high_resolution_clock::now();

        s += std::chrono::duration_cast<std::chrono::nanoseconds>(t2 - t1).count();
    }


    std::cout << (1000000000.f * static_cast<double>(TRIALS) / s) << std::endl;

    return 0;
}


template float & matrix_t::operator()(std::size_t, std::size_t);
