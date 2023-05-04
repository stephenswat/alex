#pragma once

#include <array>
#include <concepts>
#include <tuple>

namespace alex::concepts {
template <typename T, std::size_t N>
concept array = requires
{
    typename T::value_type;
    typename T::pointer_type;

    requires std::
        same_as<typename T::value_type, typename T::pointer_type::value_type>;

    requires requires(const T m)
    {
        {
            m.get_size()
        } -> std::same_as<std::array<std::size_t, N>>;

        requires requires(std::array<std::size_t, N> i)
        {
            {
                m.load(i)
            } -> std::same_as<typename T::value_type>;

            {
                std::apply(
                    []<typename... Q>(const T & m2, Q... ts) {
                        return m2.load(ts...);
                    },
                    std::tuple_cat(std::make_tuple(m), i)
                )
            } -> std::same_as<typename T::value_type>;
        };
    };

    requires requires(
        T m, std::array<std::size_t, N> i, typename T::value_type v
    )
    {
        {m.store(v, i)};

        {std::apply(
            []<typename... Q>(T & m2, typename T::value_type v, Q... ts) {
                m2.store(v, ts...);
            },
            std::tuple_cat(std::tie(m), std::make_tuple(v), i)
        )};
    };
};
}
