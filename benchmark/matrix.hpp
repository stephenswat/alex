#pragma once

#if !(defined(__x86_64__) && (defined(__GNUC__) || defined(__clang__)) &&        \
    defined(__BMI2__))
#error "BMI2 instruction set extension must be enabled!"
#endif

#include <x86intrin.h>
#include <climits>
#include <memory>
#include <array>

template <typename Ox, std::size_t N>
struct MortonPdepMask {
    template <std::size_t I>
    struct get_mask {
        template <typename>
        struct get_mask_helper {
        };

        template <std::size_t... Js>
        struct get_mask_helper<std::index_sequence<Js...>> {
            template <Ox S>
            struct shiftl {
                static constexpr Ox value = static_cast<Ox>(1) << S;
            };

            static constexpr Ox value =
                ((std::conditional_t<
                     Js % N == 0,
                     std::integral_constant<Ox, shiftl<Js>::value>,
                     std::integral_constant<Ox, 0>>::value) |
                 ...);
        };

        static constexpr Ox value =
            get_mask_helper<
                std::make_index_sequence<CHAR_BIT * sizeof(Ox)>>::value
            << I;
    };

    template <typename C, std::size_t... Idxs>
    static constexpr Ox compute(C c, std::index_sequence<Idxs...>)
    {
        return (_pdep_u64(c[Idxs], get_mask<Idxs>::value) | ...);
    }

    template <typename C, typename Ids = std::make_index_sequence<N>>
    static constexpr Ox compute(C c)
    {
        return compute(std::forward<C>(c), Ids{});
    }
};

template<typename T>
class Matrix {
    using mask_t = MortonPdepMask<std::size_t, 2>;

    T& operator()(std::size_t i, std::size_t j)
        {
            return m_data[mask_t::compute(std::array<std::size_t, 2>{i, j})];
        }

    const T& operator()(std::size_t i, std::size_t j) const {
        return m_data[mask_t::compute(std::array<std::size_t, 2>{i, j})];
    }

    private:
    std::unique_ptr<T[]> m_data;
};
