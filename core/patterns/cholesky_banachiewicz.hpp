#pragma once

#include <cmath>
#include <cstddef>

#include "concepts/array.hpp"

namespace alex::patterns {
template <concepts::array<2> M>
void cholesky_banachiewicz(const M & A, M & L)
{
    auto [m, n] = A.get_size();

    assert(m == n);

    for (std::size_t i = 0; i < m; ++i) {
        for (std::size_t j = 0; j <= i; ++j) {
            typename M::value_type sum = 0;

            for (std::size_t k = 0; k < j; ++k) {
                sum += L.load(i, k) * L.load(j, k);
            }

            if (i == j)
                L.store(std::sqrt(A.load(i, i) - sum), i, j);
            else
                L.store(
                    static_cast<typename M::value_type>(1.0) / L.load(j, j) *
                        (A.load(i, i) - sum),
                    i,
                    j
                );
        }
    }
}
}
