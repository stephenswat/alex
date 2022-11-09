#pragma once

template<typename>
struct maximum{};

template<std::size_t Idx>
struct maximum<std::index_sequence<Idx>> {
    static constexpr std::size_t value = Idx;
};

template<std::size_t Idx, std::size_t ... Idxs>
struct maximum<std::index_sequence<Idx, Idxs...>> {
    static constexpr std::size_t value = std::max(
                Idx,
                maximum<std::index_sequence<Idxs...>>::value
            );
};

template<typename, std::size_t>
struct count{};

template<std::size_t ... Idxs, std::size_t I>
struct count<std::index_sequence<Idxs...>, I> {
    static constexpr std::size_t value = ((Idxs == I ? 1 : 0) + ...);
};

template<typename, typename>
struct morton_index {};

template <std::size_t ... Idxs, typename Ox>
struct morton_index<std::index_sequence<Idxs...>, Ox> {
    static constexpr std::size_t N = maximum<std::index_sequence<Idxs...>>::value + 1;

    static_assert(std::is_unsigned_v<Ox>, "Index ype must be unsigned integer.");
    static_assert(sizeof(Ox) == 4 || sizeof(Ox) == 8, "Index type must be 4 or 8 bytes.");

    template <std::size_t I>
    struct get_mask {
        template <typename, typename>
        struct get_mask_helper {
        };

        template <std::size_t... Jdxs, std::size_t... Kdxs>
        struct get_mask_helper<std::index_sequence<Jdxs...>, std::index_sequence<Kdxs...>> {
            static constexpr Ox value = (((Jdxs == I ? static_cast<Ox>(1) : static_cast<Ox>(0)) << Kdxs) | ...);
        };

        static constexpr Ox value =
            get_mask_helper<std::index_sequence<Idxs...>, std::make_index_sequence<sizeof...(Idxs)>>::value;
    };

    template <typename C, std::size_t... Jdxs>
    static constexpr Ox compute(C c, std::index_sequence<Jdxs...>)
    {
        if constexpr (sizeof(Ox) == 8) {
            return (_pdep_u64(c[Jdxs], get_mask<Jdxs>::value) | ...);
        } else {
            return (_pdep_u32(c[Jdxs], get_mask<Jdxs>::value) | ...);
        }
    }

    template <typename C, typename Jdxs = std::make_index_sequence<N>>
    static constexpr Ox compute(C c)
    {
        return compute(std::forward<C>(c), Jdxs{});
    }
};
