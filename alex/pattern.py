import typing

import __alex_core
import alex.definitions
import alex.schema
import alex.simulator


def runPattern(
    pattern: alex.definitions.Pattern,
    hierarchy: alex.schema.CacheHierarchy,
    permutation: typing.List[int],
    precision: alex.definitions.Precision = alex.definitions.Precision.Single,
) -> alex.simulator.CacheSimulator:
    sim = alex.simulator.CacheSimulator(hierarchy)

    getattr(__alex_core, "_{}_{}_sim_entry".format(str(pattern), str(precision)))(
        sim._sim.first_level.backend, permutation
    )

    sim._sim.force_write_back()

    return sim


def runBenchPattern(
    pattern: alex.definitions.Pattern,
    permutation: typing.List[int],
    precision: alex.definitions.Precision = alex.definitions.Precision.Single,
) -> alex.simulator.CacheSimulator:
    return getattr(
        __alex_core, "_{}_{}_bench_entry".format(str(pattern), str(precision))
    )(permutation)
