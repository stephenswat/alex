#pragma once

#include <cstddef>

#include "concepts/matrix.hpp"

namespace alex::patterns {
template <concepts::matrix M>
void mm_ikj(const M & A, const M & B, M & C)
{
    auto [m, n] = C.get_size();

    for (std::size_t i = 0; i < m; ++i) {
        for (std::size_t k = 0; k < n; ++k) {
            for (std::size_t j = 0; j < m; ++j) {
                C.store(i, j, C.load(i, j) + A.load(i, k) * B.load(k, j));
            }
        }
    }
}
}
