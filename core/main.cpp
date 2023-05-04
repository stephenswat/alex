#define PYBIND11_DETAILED_ERROR_MESSAGES

#include <array>
#include <concepts>
#include <iostream>
#include <type_traits>
#include <utility>

#include <pybind11/pybind11.h>
#include <pybind11/stl.h>

#include "arrays/lexicographic.hpp"
#include "arrays/shuffle_rt.hpp"
#include "cachesim.hpp"
#include "patterns/cholesky_banachiewicz.hpp"
#include "patterns/himeno.hpp"
#include "patterns/jacobi2d.hpp"
#include "patterns/mm_ijk.hpp"
#include "patterns/mm_ikj.hpp"
#include "pointers/simulated_pointer.hpp"
#include "utils/pdep.hpp"

template <std::size_t N>
std::array<std::size_t, N> size_getter(const std::vector<std::size_t> & ind)
{
    std::array<std::size_t, N> out;

    for (std::size_t i = 0; i < N; ++i) {
        out[i] = 1;
    }

    for (const std::size_t i : ind) {
        out[i] <<= 1;
    }

    return out;
}

template <std::floating_point T>
void _MMijk_entry(
    pybind11::handle obj, const std::vector<std::size_t> & individual
)
{
    Cache & cache = *reinterpret_cast<Cache *>(obj.ptr());

    auto [m, n] = size_getter<2>(individual);

    auto [_A, _B, _C] =
        alex::pointers::partition<T, T, T>(cache, {m * n, m * n, m * n});

    alex::arrays::shuffle_rt<2, decltype(_A)> A(std::move(_A), individual),
        B(std::move(_B), individual), C(std::move(_C), individual);

    alex::patterns::mm_ijk(A, B, C);
}

template <std::floating_point T>
void _MMikj_entry(
    pybind11::handle obj, const std::vector<std::size_t> & individual
)
{
    Cache & cache = *reinterpret_cast<Cache *>(obj.ptr());

    auto [m, n] = size_getter<2>(individual);

    auto [_A, _B, _C] =
        alex::pointers::partition<T, T, T>(cache, {m * n, m * n, m * n});

    alex::arrays::shuffle_rt<2, decltype(_A)> A(std::move(_A), individual),
        B(std::move(_B), individual), C(std::move(_C), individual);

    alex::patterns::mm_ikj(A, B, C);
}

template <std::floating_point T>
void _Jacobi2D_entry(
    pybind11::handle obj, const std::vector<std::size_t> & individual
)
{
    Cache & cache = *reinterpret_cast<Cache *>(obj.ptr());

    auto [m, n] = size_getter<2>(individual);

    auto [_A, _B] = alex::pointers::partition<T, T>(cache, {m * n, m * n});

    alex::arrays::shuffle_rt<2, decltype(_A)> A(std::move(_A), individual),
        B(std::move(_B), individual);

    alex::patterns::jacobi2d(A, B);
}

template <std::floating_point T>
void _Cholesky_entry(
    pybind11::handle obj, const std::vector<std::size_t> & individual
)
{
    Cache & cache = *reinterpret_cast<Cache *>(obj.ptr());

    auto [m, n] = size_getter<2>(individual);

    auto [_A, _B] = alex::pointers::partition<T, T>(cache, {m * n, m * n});

    alex::arrays::shuffle_rt<2, decltype(_A)> A(std::move(_A), individual),
        B(std::move(_B), individual);

    alex::patterns::cholesky_banachiewicz(A, B);
}

template <std::floating_point T>
void _Himeno_entry(
    pybind11::handle obj, const std::vector<std::size_t> & individual
)
{

    Cache & cache = *reinterpret_cast<Cache *>(obj.ptr());

    auto [m, n, p] = size_getter<3>(individual);

    auto [_A, _B, _C, _P, _W1, _W2] = alex::pointers::partition<
        std::array<T, 3>,
        std::array<T, 3>,
        std::array<T, 3>,
        T,
        T,
        T>(
        cache,
        {m * n * p, m * n * p, m * n * p, m * n * p, m * n * p, m * n * p}
    );

    alex::arrays::shuffle_rt<3, decltype(_A)> A(std::move(_A), individual),
        B(std::move(_B), individual), C(std::move(_C), individual);

    alex::arrays::shuffle_rt<3, decltype(_P)> P(std::move(_P), individual),
        W1(std::move(_W1), individual), W2(std::move(_W2), individual);

    alex::patterns::himeno(A, B, C, P, W1, W2);
}

#define GLUE_HELPER(x, y) x##y
#define GLUE(x, y) GLUE_HELPER(x, y)

#define REGISTER(NAME)                                                         \
    do {                                                                       \
        m.def(                                                                 \
            "_" #NAME "_double_entry", &GLUE(_, GLUE(NAME, _entry)) < double > \
        );                                                                     \
        m.def(                                                                 \
            "_" #NAME "_single_entry", &GLUE(_, GLUE(NAME, _entry)) < float >  \
        );                                                                     \
    } while (0)

PYBIND11_MODULE(__alex_core, m)
{
    REGISTER(MMijk);
    REGISTER(MMikj);
    REGISTER(Jacobi2D);
    REGISTER(Cholesky);
    REGISTER(Himeno);
}
