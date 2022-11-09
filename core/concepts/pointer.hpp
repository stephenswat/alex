#pragma once

#include <concepts>

namespace alex::concepts {
template <typename T>
concept pointer = requires
{
    typename T::value_type;

    requires requires(const T p, std::size_t i)
    {
        {
            p.load(i)
        } -> std::same_as<typename T::value_type>;
    };

    requires requires(T p, std::size_t i, typename T::value_type v)
    {
        {p.store(i, v)};
    };
};
}
