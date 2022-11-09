#pragma once

#include <array>
#include <cstddef>
#include <utility>

template <typename T, std::size_t N, std::size_t... Is>
std::array<T, N - 1>
tail_impl(const std::array<T, N> & i, const std::index_sequence<Is...> &)
{
    return {i[Is + 1]...};
}

template <typename T, std::size_t N>
std::array<T, N - 1> tail(const std::array<T, N> & i)
{
    return tail_impl(i, std::make_index_sequence<N - 1>());
}
