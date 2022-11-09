#pragma once

#include <climits>
#include <concepts>

#include <x86intrin.h>

template <std::unsigned_integral T>
inline T pdep(const T & v, const T & m)
{
#ifdef __BMI2__
    return _pdep_u64(v, m);
#else
    T a = 0;

    for (unsigned i = 0, j = 0; i < sizeof(T) * CHAR_BIT; ++i) {
        if (m & (1UL << i)) {
            a |= ((v >> j) & 1UL) << i;
            ++j;
        }
    }

    return a;
#endif
}
