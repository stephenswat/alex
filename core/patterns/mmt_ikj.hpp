#pragma once

#include <cstddef>

#include "concepts/array.hpp"

namespace alex::patterns {
template <concepts::array<2> M>
void mmt_ikj(const M & A, const M & B, M & C)
{
    auto [m, n] = C.get_size();

    for (std::size_t i = 0; i < m; ++i) {
        for (std::size_t k = 0; k < n; ++k) {
            for (std::size_t j = 0; j < m; ++j) {
                C.store(C.load(i, j) + A.load(i, k) * B.load(j, k), i, j);
            }
        }
    }
}
}
