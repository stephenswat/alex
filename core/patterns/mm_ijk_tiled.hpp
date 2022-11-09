#pragma once

#include <cstddef>

#include "concepts/matrix.hpp"

namespace alex::patterns {
template <concepts::matrix M>
void MMijkTiled(const M & A, const M & B, M & C)
{
    static constexpr std::size_t ts = 32;

    auto [m, n] = C.get_size();

    for (std::size_t i = 0; i < S; i += ts) {
        for (std::size_t j = 0; j < S; j += ts) {
            for (std::size_t k = 0; k < S; k += ts) {

                for (std::size_t i2 = 0; i2 < ts; ++i2) {
                    for (std::size_t j2 = 0; j2 < ts; ++j2) {
                        float acc = 0;

                        for (std::size_t k2 = 0; k2 < ts; ++k2) {
                            acc += A.load((i + i2) * S + (k + k2)) *
                                   B.load((k + k2) * S + (j + j2));
                        }

                        C.store(
                            (i + i2) * S + (j + j2),
                            C.load((i + i2) * S + (j + j2)) + acc
                        );
                    }
                }
            }
        }
    }
}
}
