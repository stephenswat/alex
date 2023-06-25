#pragma once

#include <cstddef>

#include "concepts/array.hpp"

namespace alex::patterns {
template <concepts::array<2> M>
void mm_ijk(const M & A, const M & B, M & C)
{
    const auto [m, n] = C.get_size();

    for (std::size_t i = 0; i < m; ++i) {
        for (std::size_t j = 0; j < m; ++j) {
            typename M::value_type acc = 0.;

            for (std::size_t k = 0; k < n; ++k) {
                acc += A.load(i, k) * B.load(k, j);
            }

            C.store(acc, i, j);
        }
    }
}
}
