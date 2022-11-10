#include <chrono>
#include <cstdlib>
#include <iostream>

#include "matrix.hpp"

using matrix_t = matrix<std::index_sequence<PERMUTATION>>;

std::size_t benchmark_MMijk() {
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

        return std::chrono::duration_cast<std::chrono::nanoseconds>(t2 - t1).count();
}

std::size_t benchmark_MMbijk() {
        matrix_t a = matrix_t::random();
        matrix_t b = matrix_t::random();
        matrix_t c;

        std::chrono::high_resolution_clock::time_point t1 = std::chrono::high_resolution_clock::now();
        
        static constexpr std::size_t bs = 16;
        for (std::size_t i0 = 0; i0 < matrix_t::N; i0 += bs) {
            for (std::size_t j0 = 0; j0 < matrix_t::N; j0 += bs) {
                for (std::size_t k0 = 0; k0 < matrix_t::N; k0 += bs) {

                    for (std::size_t j1 = j0; j1 < j0 + bs; ++j1) {
                        for (std::size_t i1 = i0; i1 < i0 + bs; ++i1) {
                            float acc = 0.f;

                            for (std::size_t k1 = k0; k1 < k0 + bs; ++k1) {
                                acc += a(i1, k1) * b(k1, j1);
                            }

                            c(i1, j1) += acc;
                        }
                    }
                }
            }
        }

        std::chrono::high_resolution_clock::time_point t2 = std::chrono::high_resolution_clock::now();

        return std::chrono::duration_cast<std::chrono::nanoseconds>(t2 - t1).count();
}

int main() {
    std::size_t warmup = 10000;
    std::size_t trials = 100000;


    volatile std::size_t s = 0;

    for (int t = 0; t < warmup + trials; ++t) {
        volatile std::size_t r = benchmark_MMbijk();

        if (t >= warmup) {
            s += benchmark_MMbijk();
        }
    }


    std::cout << (matrix_t::N * matrix_t::N * matrix_t::N * static_cast<double>(trials) / s) << std::endl;

    return 0;
}

