#pragma once

#include <cstddef>

#include "concepts/matrix.hpp"

namespace alex::patterns {
template <concepts::matrix M>
void stride2d(const M & A, std::size_t dx, std::size_t dy, std::size_t i)
{
    auto [m, n] = A.get_size();

    std::size_t x = 0, y = 0;

    for (std::size_t j = 0; j < i; ++j) {
        A.load(x, y);

        x = (x + dx) % m;
        y = (y + dy) % (n - 1);
    }
}
}
