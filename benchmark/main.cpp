#include <chrono>
#include <cstdlib>
#include <iostream>


#ifndef PERMUTATION
#error "Permutation is not defined!"
#endif

using matrix_t = matrix<std::index_sequence<PERMUTATION>>;

concept Matrix {}

template<Matrix M>
void benchmark_MMijk(const M & a,const  M & b, M& c) {
    for (std::size_t i = 0; i < matrix_t::N; ++i) {
        for (std::size_t j = 0; j < matrix_t::M; ++j) {
            float acc = 0.f;

            for (std::size_t k = 0; k < matrix_t::N; ++k) {
                acc += a.load(i, k) * b.load(k, j);
            }

            c.store(i, j, acc);
        }
    }
}

template<Matrix M>
void benchmark_MMikj(const M & a,const  M & b, M& c) {
    for (std::size_t i = 0; i < matrix_t::N; ++i) {
        for (std::size_t j = 0; j < matrix_t::M; ++j) {
            float acc = 0.f;

            for (std::size_t k = 0; k < matrix_t::N; ++k) {
                acc += a.load(i, k) * b.load(k, j);
            }

            c.store(i, j, acc);
        }
    }
}

template<Matrix M>
void benchmark_Jacobi2D() {}

template<Matrix M>
void benchmark_ADI() {}

template<Matrix M>
void benchmark_Cholesky() {}

int main() {
    std::size_t warmup = 10000;
    std::size_t trials = 100000;


    volatile std::size_t s = 0;

    matrix_t a = matrix_t::random();
    matrix_t b = matrix_t::random();
    matrix_t c = matrix_t::random();

    for (int t = 0; t < warmup + trials; ++t) {
        std::chrono::high_resolution_clock::time_point t1 = std::chrono::high_resolution_clock::now();
        benchmark_MMijk(a, b, c);
        std::chrono::high_resolution_clock::time_point t2 = std::chrono::high_resolution_clock::now();

        if (t >= warmup) {
            s += std::chrono::duration_cast<std::chrono::nanoseconds>(t2 - t1).count();
        }
    }

    std::cout << (matrix_t::N * matrix_t::N * matrix_t::N * static_cast<double>(trials) / s) << std::endl;

    return 0;
}
