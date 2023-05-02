#pragma once

#include <cstddef>

#include "concepts/matrix.hpp"

namespace alex::patterns {
template <concepts::matrix M>
void jacobi2d(const M & A, M & B)
{
    auto [m, n] = B.get_size();

    for (std::size_t k = 0; k < 3; ++k) {
    for (std::size_t i = 0; i < m; ++i) {
        for (std::size_t j = 0; j < n; ++j) {
            typename M::value_type v1, v2, v3, v4;

            if (i > 0) {
                v1 = A.load(i - 1, j);
            } else {
                v1 = 0.f;
            }

            if (j > 0) {
                v2 = A.load(i, j - 1);
            } else {
                v2 = 0.f;
            }

            if (i < m - 1) {
                v3 = A.load(i + 1, j);
            } else {
                v3 = 0.f;
            }

            if (j < n - 1) {
                v4 = A.load(i, j + 1);
            } else {
                v4 = 0.f;
            }

            B.store(i, j, 0.25f * (v1 + v2 + v3 + v4));
        }
    }
    }
}
}
