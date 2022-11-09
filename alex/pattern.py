import typing

import __alex_core
import alex.schema
import alex.simulator


def MMijk(
    hierarchy: alex.schema.CacheHierarchy, permutation: typing.List[int]
) -> alex.simulator.CacheSimulator:
    sim = alex.simulator.CacheSimulator(hierarchy)

    __alex_core._MMijk_entry(sim._sim.first_level.backend, permutation)

    sim._sim.force_write_back()

    return sim


def Jacobi2D(
    hierarchy: alex.schema.CacheHierarchy, permutation: typing.List[int]
) -> alex.simulator.CacheSimulator:
    sim = alex.simulator.CacheSimulator(hierarchy)

    __alex_core._Jacobi2D_entry(sim._sim.first_level.backend, permutation)

    sim._sim.force_write_back()

    return sim


def Stride2D(
    hierarchy: alex.schema.CacheHierarchy, permutation: typing.List[int]
) -> alex.simulator.CacheSimulator:
    sim = alex.simulator.CacheSimulator(hierarchy)

    __alex_core._Stride2D_entry(sim._sim.first_level.backend, permutation)

    sim._sim.force_write_back()

    return sim
