#pragma once

#include <cassert>
#include <iostream>

#include "concepts/pointer.hpp"
#include "utils/mask.hpp"
#include "utils/pdep.hpp"

namespace alex::arrays {
template <std::size_t N, concepts::pointer T>
class shuffle_rt
{
public:
    using pointer_type = T;
    using value_type = typename pointer_type::value_type;

    shuffle_rt(T && _p, const std::vector<std::size_t> & _c)
        : ptr(std::forward<T>(_p))
        , m(utils::get_masks<N>(_c))
        , s(utils::get_sizes<N>(_c))
    {
    }

    template <std::unsigned_integral... I>
    inline typename T::value_type load(const I &... is) const
    {
        return load(std::array<std::size_t, N>{is...});
    }

    inline typename T::value_type load(const std::array<std::size_t, N> & i
    ) const
    {
        assert(i < s1 && j < s2);
        return ptr.load(get_index(i));
    }

    template <std::unsigned_integral... I>
    inline void store(const typename T::value_type & v, const I &... is)
    {
        return store(v, std::array<std::size_t, N>{is...});
    }

    inline void store(
        const typename T::value_type & v, const std::array<std::size_t, N> & i
    )
    {
        // assert(i < s1 && j < s2);
        ptr.store(get_index(i), v);
    }

    std::array<std::size_t, N> get_size() const
    {
        return s;
    }

private:
    template <std::size_t... J>
    inline std::size_t
    get_index_helper(const std::array<std::size_t, N> & i, std::index_sequence<J...>)
        const
    {
        return (pdep(i[J], m[J]) | ...);
    }

    template <std::unsigned_integral... I>
    inline std::size_t get_index(const std::array<std::size_t, N> & i) const
    {
        return get_index_helper(i, std::make_index_sequence<N>());
    }

    T ptr;
    const std::array<std::size_t, N> m, s;
};
}
