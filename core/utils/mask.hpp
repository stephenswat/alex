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

template <std::size_t N, std::size_t... I>
std::array<std::size_t, N>
get_masks_helper(const std::vector<std::size_t> & p, std::index_sequence<I...>)
{
    return {get_mask<std::size_t>(p, I)...};
}

template <std::size_t N>
std::array<std::size_t, N> get_masks(const std::vector<std::size_t> & p)
{
    return get_masks_helper<N>(p, std::make_index_sequence<N>());
}

std::size_t get_size(const std::vector<std::size_t> & p, std::size_t i)
{
    std::size_t r = 1;

    for (std::size_t j : p) {
        if (i == j) {
            r <<= 1;
        }
    }

    return r;
}

template <std::size_t N, std::size_t... I>
std::array<std::size_t, N>
get_sizes_helper(const std::vector<std::size_t> & p, std::index_sequence<I...>)
{
    return {get_size(p, I)...};
}

template <std::size_t N>
std::array<std::size_t, N> get_sizes(const std::vector<std::size_t> & p)
{
    return get_sizes_helper<N>(p, std::make_index_sequence<N>());
}
}
