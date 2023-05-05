import enum
import typing

import __alex_core
import alex.schema
import alex.simulator


class Pattern(str, enum.Enum):
    MMijk = "MMijk"
    MMikj = "MMikj"
    MMTijk = "MMTijk"
    MMTikj = "MMTikj"
    Jacobi2D = "Jacobi2D"
    Himeno = "Himeno"
    Cholesky = "Cholesky"
    Crout = "Crout"

    def __str__(self):
        return self.value


class Precision(str, enum.Enum):
    Single = "single"
    Double = "double"

    def __str__(self):
        return self.value


def runPattern(
    pattern: Pattern,
    hierarchy: alex.schema.CacheHierarchy,
    permutation: typing.List[int],
    precision: Precision = Precision.Single,
) -> alex.simulator.CacheSimulator:
    sim = alex.simulator.CacheSimulator(hierarchy)

    getattr(__alex_core, "_{}_{}_entry".format(str(pattern), str(precision)))(
        sim._sim.first_level.backend, permutation
    )

    sim._sim.force_write_back()

    return sim
