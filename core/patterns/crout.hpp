#pragma once

#include <cmath>
#include <cstddef>
#include <memory>

#include "concepts/array.hpp"

namespace alex::patterns {
template <concepts::array<2> M>
void crout(const M & A, M & L, M & U)
{
    auto [m, n] = A.get_size();

    assert(m == n);

    for (std::size_t i = 0; i < n; ++i) {
        U.store(1.0, i, i);
    }

    for (std::size_t j = 0; j < n; ++j) {
        for (std::size_t i = j; i < n; ++i) {
            typename M::value_type sum = 0;

            for (std::size_t k = 0; k < j; ++k) {
                sum += L.load(i, k) * U.load(k, j);
            }

            L.store(A.load(i, j) - sum, i, j);
        }

        for (std::size_t i = j; i < n; ++i) {
            typename M::value_type sum = 0;

            for (std::size_t k = 0; k < j; ++k) {
                sum += L.load(j, k) * U.load(k, i);
            }

            U.store((A.load(j, i) - sum) / L.load(j, j), j, i);
        }
    }
}
}
