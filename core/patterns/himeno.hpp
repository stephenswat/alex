#pragma once

#include <cmath>
#include <concepts>
#include <cstddef>

#include "concepts/array.hpp"

namespace alex::patterns {
template <concepts::array<3> M, concepts::array<3> N>
void himeno(
    const M & A, const M & B, const M & C, const N & P, const N & W1, N & W2
) requires
    std::same_as<typename M::value_type::value_type, typename N::value_type>
{
    auto [m, n, p] = W2.get_size();

    for (std::size_t i = 1; i < m - 1; ++i) {
        for (std::size_t j = 1; j < n - 1; ++j) {
            for (std::size_t k = 1; k < p - 1; ++k) {
                typename M::value_type vA = A.load(i, j, k);
                typename M::value_type vB = B.load(i, j, k);
                typename M::value_type vC = C.load(i, j, k);

                typename N::value_type s0 =
                    vA[0] * P.load(i, j, k) + vA[1] * P.load(i, j + 1, k) +
                    vA[2] * P.load(i, j, k + 1) +
                    vB[0] *
                        (P.load(i + 1, j + 1, k) - P.load(i + 1, j - 1, k) -
                         P.load(i - 1, j + 1, k) + P.load(i - 1, j - 1, k)) +
                    vB[1] *
                        (P.load(i, j + 1, k + 1) - P.load(i, j - 1, k + 1) -
                         P.load(i, j + 1, k - 1) + P.load(i, j - 1, k - 1)) +
                    vB[2] *
                        (P.load(i + 1, j, k + 1) - P.load(i - 1, j, k + 1) -
                         P.load(i + 1, j, k - 1) + P.load(i - 1, j, k - 1)) +
                    vC[0] * P.load(i - 1, j, k) + vC[1] * P.load(i, j - 1, k) +
                    vC[2] * P.load(i, j, k - 1) + W1.load(i, j, k);

                auto ss = ((s0 / 6.0f) - P.load(i, j, k));

                W2.store(P.load(i, j, k) + 0.8 * ss, i, j, k);
            }
        }
    }
}
}
