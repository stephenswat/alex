#define PYBIND11_DETAILED_ERROR_MESSAGES

#include <array>
#include <iostream>
#include <type_traits>
#include <utility>
#include <concepts>

#include <pybind11/pybind11.h>
#include <pybind11/stl.h>

#include "arrays/lexicographic.hpp"
#include "arrays/shuffle_rt.hpp"
#include "cachesim.hpp"
#include "patterns/jacobi2d.hpp"
#include "patterns/mm_ijk.hpp"
#include "patterns/mm_ikj.hpp"
#include "patterns/stride2d.hpp"
#include "pointers/simulated_pointer.hpp"
#include "utils/pdep.hpp"

template<std::floating_point T>
void _MMijk_entry(
    pybind11::handle obj, const std::vector<std::size_t> & individual
)
{
    Cache & cache = *reinterpret_cast<Cache *>(obj.ptr());

    std::size_t mb = 0, nb = 0;

    for (const std::size_t i : individual) {
        if (i == 0) {
            mb++;
        } else if (i == 1) {
            nb++;
        } else {
            std::cerr << "Invalid digit in individual!" << std::endl;
        }
    }

    std::size_t m = 1UL << mb;
    std::size_t n = 1UL << nb;

    auto [_A, _B, _C] = alex::pointers::partition<T, T, T>(
        cache, {m * n, m * n, m * n}
    );

    alex::arrays::shuffle_rt<decltype(_A)> A(std::move(_A), individual),
        B(std::move(_B), individual), C(std::move(_C), individual);

    alex::patterns::mm_ijk(A, B, C);
}

template<std::floating_point T>
void _Jacobi2D_entry(
    pybind11::handle obj, const std::vector<std::size_t> & individual
)
{
    Cache & cache = *reinterpret_cast<Cache *>(obj.ptr());

    std::size_t mb = 0, nb = 0;

    for (const std::size_t i : individual) {
        if (i == 0) {
            mb++;
        } else if (i == 1) {
            nb++;
        } else {
            std::cerr << "Invalid digit in individual!" << std::endl;
        }
    }

    std::size_t m = 1UL << mb;
    std::size_t n = 1UL << nb;

    auto [_A, _B] =
        alex::pointers::partition<T, T>(cache, {m * n, m * n});

    alex::arrays::shuffle_rt<decltype(_A)> A(std::move(_A), individual),
        B(std::move(_B), individual);

    alex::patterns::jacobi2d(A, B);
}

PYBIND11_MODULE(__alex_core, m)
{
    m.def("_MMijk_entry", &_MMijk_entry<double>, "Heyooo");
    m.def("_Jacobi2D_entry", &_Jacobi2D_entry<double>, "Heyooo");
}
