#pragma once

#include <concepts>

#include "concepts/pointer.hpp"

namespace alex::arrays {
template <std::size_t N, concepts::pointer T>
class lexicographic
{
public:
    using pointer_type = T;
    using value_type = typename pointer_type::value_type;

    template <std::unsigned_integral... I>
    lexicographic(T && _p, const I &... _s) requires(sizeof...(I) == N)
        : ptr(_p)
        , s{_s...}
    {
    }

    template <std::unsigned_integral... I>
    inline typename T::value_type load(const I &... ts) const
        requires(sizeof...(I) == N)
    {
        return ptr.load(get_index(ts...));
    }

    inline typename T::value_type load(const std::array<std::size_t, 2> & i
    ) const
    {
        assert(i < m && j < n);
        return ptr.load(get_index(i[0], i[1]));
    }

    inline void store(
        const typename T::value_type & v,
        const std::size_t & i,
        const std::size_t & j
    )
    {
        assert(i < m && j < n);
        ptr.store(get_index(i, j), v);
    }

    std::array<std::size_t, N> get_size() const
    {
        return s;
    }

private:
    inline std::size_t
    get_index_helper(const std::array<std::size_t, N> & i, std::size_t j) const
    {
        if (j < N - 1) {
            return i[j] + s[j] * get_index_helper(i, j + 1);
        } else {
            return i[j];
        }
    }

    inline std::size_t get_index(const std::array<std::size_t, N> & i) const
    {
        return get_index_helper(i, 0);
    }

    T ptr;
    std::array<std::size_t, N> s;
};
}
