import argparse
import collections
import concurrent.futures
import csv
import os
import pathlib
import random
import time

import yaml

import alex.ga
import alex.pattern
import alex.schema
import alex.simulator


def enumerateOccurances(i):
    c = collections.defaultdict(int)
    r = []

    for x in i:
        r.append((x, c[x]))
        c[x] += 1

    return r


def cxGeneralizedOrdered(ind1, ind2):
    idx = random.randint(0, len(ind1))
    num = random.randint(1, len(ind1) // 2)

    e1 = enumerateOccurances(ind1)
    e2 = enumerateOccurances(ind2)

    p = (e2 + e2)[idx : idx + num]

    assert len(p) == num

    i = [x for x in e1[:idx] if x not in p] + p + [x for x in e1[idx:] if x not in p]

    r = [j for (j, _) in i]

    assert collections.Counter(ind1) == collections.Counter(r) and collections.Counter(
        ind2
    ) == collections.Counter(r)

    nind = tuple(r)

    # assert(nind != ind1 and nind != ind2)

    return nind


def mutExchangeDifferent(ind):
    size = len(ind)

    nind = list(ind)

    while True:
        i = random.randint(0, size - 1)
        j = random.randint(0, size - 1)

        if nind[i] != nind[j]:
            break

    nind[i], nind[j] = nind[j], nind[i]

    assert tuple(nind) != ind

    return tuple(nind)


def initialPop(*mtpl):
    """Generate the initial permutation population.

    Generate the initial population of our permutations. We generate the two
    canonical lexigraphic permutations and use these to perform genetic
    operations.

    This function takes as arguments the number of bits in each dimension,
    where the number of dimensions is variable. For example, argument list [3,
    3] generates the permutations [aaabbb, bbbaaa]. Similarly, argument [2, 2,
    2] generates permutations [aabbcc, ccbbaa].
    """

    q = [i for (i, j) in enumerate(mtpl) for _ in range(j)]

    return [tuple(q), tuple(q[::-1])]


def evalFitness(individual, hierarchy):
    simulator = alex.pattern.Jacobi2D(hierarchy, individual)
    accesses = (
        simulator._sim.first_level.backend.LOAD_count
        + simulator._sim.first_level.backend.STORE_count
    )

    cycles = 0

    for x in simulator._sim.levels():
        cycles += x.stats()["HIT_count"] * x.latency

    return accesses / cycles


def parseBits(s):
    return [int(x) for x in s.split(":")]


def main():
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "-c",
        "--cache",
        type=pathlib.Path,
        help="cache hierarchy YAML file to load",
        required=True,
    )
    parser.add_argument(
        "-b",
        "--bits",
        type=parseBits,
        help="colon-separated bit counts",
        required=True,
    )
    parser.add_argument(
        "-t",
        "--trace",
        type=str,
        help="trace type to use",
        required=True,
    )
    parser.add_argument(
        "-r",
        "--ranking",
        type=pathlib.Path,
        help="output CSV for final population",
    )
    parser.add_argument(
        "-g", "--generations", type=int, help="number of generations", default=10
    )
    parser.add_argument("-j", "--parallel", type=int, nargs="?", const=-1)

    args = parser.parse_args()

    with open(args.cache, "r") as f:
        hierarchy = alex.schema.CacheHierarchy(**yaml.safe_load(f))

    ga = alex.ga.GA(
        generations=args.generations,
        initial_population=initialPop(*args.bits),
        mutation_func=mutExchangeDifferent,
        crossover_func=cxGeneralizedOrdered,
        fitness_func=evalFitness,
        fitness_func_kwargs={"hierarchy": hierarchy},
        retained_count=20,
        generated_count=30,
        elite_count=5,
    )

    if args.parallel is not None:
        with concurrent.futures.ProcessPoolExecutor(
            max_workers=None if args.parallel < 0 else args.parallel
        ) as executor:
            ga.run(executor)
    else:
        ga.run()

    print(len(ga.fitness_cache))

    print("Final pop:")
    for i, f in sorted(ga.results(), key=lambda t: t[1], reverse=True):
        print(i, f)

    print("\n\nCache:")
    for i, f in sorted(ga.fitness_cache.items(), key=lambda t: t[1], reverse=True):
        print(i, f)
