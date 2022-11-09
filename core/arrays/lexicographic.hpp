#pragma once

#include "concepts/pointer.hpp"

namespace alex::arrays {
template <concepts::pointer T>
class lexicographic
{
public:
    using pointer_type = T;
    using value_type = typename pointer_type::value_type;

    lexicographic(T && _p, const std::size_t & _m, const std::size_t & _n)
        : ptr(_p)
        , m(_m)
        , n(_n)
    {
    }

    inline typename T::value_type
    load(const std::size_t & i, const std::size_t & j) const
    {
        assert(i < m && j < n);
        return ptr.load(get_index(i, j));
    }

    inline void store(
        const std::size_t & i,
        const std::size_t & j,
        const typename T::value_type & v
    )
    {
        assert(i < m && j < n);
        ptr.store(get_index(i, j), v);
    }

    std::tuple<std::size_t, std::size_t> get_size() const
    {
        return {m, n};
    }

private:
    inline std::size_t
    get_index(const std::size_t & i, const std::size_t & j) const
    {
        return i * n + j;
    }

    T ptr;
    std::size_t m, n;
};
}
