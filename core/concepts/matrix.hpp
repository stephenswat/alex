#pragma once

#include <concepts>

namespace alex::concepts {
template <typename T>
concept matrix = requires
{
    typename T::value_type;
    typename T::pointer_type;

    requires std::
        same_as<typename T::value_type, typename T::pointer_type::value_type>;

    requires requires(const T m)
    {
        {
            m.get_size()
        } -> std::same_as<std::tuple<std::size_t, std::size_t>>;

        requires requires(std::size_t i, std::size_t j)
        {
            {
                m.load(i, j)
            } -> std::same_as<typename T::value_type>;
        };
    };

    requires requires(
        T m, std::size_t i, std::size_t j, typename T::value_type v
    )
    {
        {m.store(i, j, v)};
    };
};
}
