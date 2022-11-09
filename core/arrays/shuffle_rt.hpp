#pragma once

#include <cassert>
#include <iostream>

#include "concepts/pointer.hpp"
#include "utils/mask.hpp"
#include "utils/pdep.hpp"

namespace alex::arrays {
template <concepts::pointer T>
class shuffle_rt
{
public:
    using pointer_type = T;
    using value_type = typename pointer_type::value_type;

    shuffle_rt(T && _p, const std::vector<std::size_t> & _c)
        : ptr(_p)
        , m1(utils::get_mask<std::size_t>(_c, 0))
        , m2(utils::get_mask<std::size_t>(_c, 1))
        , s1(1UL << utils::get_size(_c, 0))
        , s2(1UL << utils::get_size(_c, 1))
    {
    }

    inline typename T::value_type
    load(const std::size_t & i, const std::size_t & j) const
    {
        assert(i < s1 && j < s2);
        return ptr.load(get_index(i, j));
    }

    inline void store(
        const std::size_t & i,
        const std::size_t & j,
        const typename T::value_type & v
    )
    {
        assert(i < s1 && j < s2);
        ptr.store(get_index(i, j), v);
    }

    std::tuple<std::size_t, std::size_t> get_size() const
    {
        return {s1, s2};
    }

private:
    inline std::size_t
    get_index(const std::size_t & i, const std::size_t & j) const
    {
        return pdep(i, m1) | pdep(j, m2);
    }

    T ptr;
    std::size_t m1, m2;
    std::size_t s1, s2;
};
}
