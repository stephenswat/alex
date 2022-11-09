#pragma once

#include <cstddef>

#include "cachesim.hpp"
#include "utils/tail.hpp"

namespace alex::pointers {
template <typename T>
class simulated_pointer
{
public:
    using value_type = T;

    simulated_pointer(Cache & _cache, std::size_t _begin)
        : cache(_cache)
        , begin(_begin)
    {
    }

    T load(const std::size_t & i) const
    {
        Cache__load(
            &cache, {static_cast<long int>(begin + i * sizeof(T)), sizeof(T)}
        );

        return T();
    }

    void store(const std::size_t & i, const T &)
    {
        Cache__store(
            &cache, {static_cast<long int>(begin + i * sizeof(T)), sizeof(T)}, 0
        );
    }

private:
    Cache & cache;
    std::size_t begin;
};

template <typename T, typename... Ts>
std::tuple<simulated_pointer<T>, simulated_pointer<Ts>...> partition_helper(
    Cache & cache,
    const std::array<std::size_t, sizeof...(Ts) + 1> & sizes,
    std::size_t alignment,
    std::size_t current
)
{
    if (current % alignment != 0) {
        current += (alignment - (current % alignment));
    }

    assert(current % alignment == 0);

    if constexpr (sizeof...(Ts) == 0) {
        return std::tuple<simulated_pointer<T>>(
            simulated_pointer<T>(cache, current)
        );
    } else {
        return std::tuple_cat(
            std::tuple<simulated_pointer<T>>(
                simulated_pointer<T>(cache, current)
            ),
            partition_helper<Ts...>(
                cache, tail(sizes), alignment, current + (sizeof(T) * sizes[0])
            )
        );
    }
}

template <typename... Ts>
std::tuple<simulated_pointer<Ts>...> partition(
    Cache & cache,
    const std::array<std::size_t, sizeof...(Ts)> & sizes,
    std::size_t alignment = 0xFFFFFFFF
)
{
    return partition_helper<Ts...>(cache, sizes, alignment, 0UL);
}
}
