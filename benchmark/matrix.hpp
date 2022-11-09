#pragma once

#if !(defined(__x86_64__) && (defined(__GNUC__) || defined(__clang__)) &&        \
    defined(__BMI2__))
#error "BMI2 instruction set extension must be enabled!"
#endif

#include <x86intrin.h>
#include <climits>
#include <memory>
#include <array>
#include <utility>
#include <cassert>
#include "index.hpp"

template<typename P, typename T=float, typename I=std::size_t>
class matrix {
    public:
    using index_t = morton_index<P, I>;

    static_assert(maximum<P>::value == 1, "Index sequence must be one-dimensional.");

    static constexpr std::size_t NBits = count<P, 0>::value;
    static constexpr std::size_t MBits = count<P, 1>::value;

    static constexpr std::size_t N = 1UL << NBits;
    static constexpr std::size_t M = 1UL << MBits;

    matrix() : m_data(std::make_unique<T[]>(N * M)) {}

    __attribute__((always_inline)) T& operator()(I i, I j)
        {
            assert(i < N && j < M);
            return m_data[index_t::compute(std::array<I, 2>{i, j})];
        }

    __attribute__((always_inline)) const T& operator()(I i, I j) const {
        assert(i < N && j < M);
        return m_data[index_t::compute(std::array<I, 2>{i, j})];
    }

    __attribute__((always_inline)) const T load(I i, I j) const {
        assert(i < N && j < M);
        return m_data[index_t::compute(std::array<I, 2>{i, j})];
    }

    __attribute__((always_inline)) void store(I i, I j, T v) {
        assert(i < N && j < M);
        m_data[index_t::compute(std::array<I, 2>{i, j})] = v;
    }

    static matrix random() {
        matrix m;

        for (I i = 0; i < N; ++i) {
            for (I j = 0; j < M; ++j) {
                m(i, j) = static_cast<T>(5.);
            }
        }

        return m;
    }

    private:
    std::unique_ptr<T[]> m_data;
};
