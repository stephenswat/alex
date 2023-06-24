#pragma once

#include <cstddef>
#include <memory>

namespace alex::pointers {
template <typename T>
class true_pointer
{
public:
    using value_type = T;

    // true_pointer(true_pointer &&) = default;

    true_pointer(std::unique_ptr<T[]> && i)
        : ptr(std::forward<std::unique_ptr<T[]>>(i))
    {
    }

    inline T load(const std::size_t & i) const
    {
        return ptr[i];
    }

    inline void store(const std::size_t & i, const T & v)
    {
        ptr[i] = v;
    }

private:
    std::unique_ptr<T[]> ptr;
};

template <typename... Ts, std::size_t... Is>
std::tuple<true_pointer<Ts>...>
allocate_multiple_helper(const std::array<std::size_t, sizeof...(Ts)> & sizes, std::index_sequence<Is...>)
{
    return {true_pointer<Ts>(std::make_unique<Ts[]>(sizes[Is]))...};
}

template <typename... Ts>
std::tuple<true_pointer<Ts>...>
allocate_multiple(const std::array<std::size_t, sizeof...(Ts)> & sizes)
{
    return allocate_multiple_helper<Ts...>(
        sizes, std::make_index_sequence<sizeof...(Ts)>()
    );
}
}
