#pragma once

#include <climits>
#include <concepts>
#include <vector>

namespace alex::utils {
template <std::unsigned_integral T>
T get_mask(const std::vector<std::size_t> & p, std::size_t i)
{
    T r = 0;

    for (std::size_t j = 0; j < std::min(p.size(), sizeof(T) * CHAR_BIT); ++j) {
        if (p[j] == i) {
            r |= 1UL << j;
        }
    }

    return r;
}

std::size_t get_size(const std::vector<std::size_t> & p, std::size_t i)
{
    std::size_t r = 0;

    for (std::size_t j : p) {
        if (i == j) {
            ++r;
        }
    }

    return r;
}
}
