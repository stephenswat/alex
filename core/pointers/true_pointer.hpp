#pragma once

#include <cstddef>
#include <memory>

namespace alex::pointers {
template <typename T>
class true_pointer
{
public:
    using value_type = T;

    true_pointer(std::unique_ptr<T[]> & i)
        : ptr(i.get())
    {
    }

    inline T load(const std::size_t & i)
    {
        return ptr[i];
    }

    inline void store(const std::size_t & i, const T & v)
    {
        ptr[i] = v;
    }

private:
    T * ptr;
};
}
