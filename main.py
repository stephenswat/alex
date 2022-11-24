import numpy
import random
import tempfile
import argparse
import subprocess
import string
import pathlib
import os
import logging
import collections
import itertools
import cachesim
import deap.creator
import deap.base
import deap.tools
import deap.algorithms
import yaml
import enum
import scoop.futures
import scoop.shared
import csv
import scoop
import functools
import operator

class AccessVerb(enum.Enum):
    LOAD = 0
    STORE = 1


class Data:
    def __init__(self, sizes, element, addr):
        self.sizes = sizes
        self.element = element
        self.addr = addr


class TraceMMijk:
    def __init__(self, size, element_size=4):
        self.__size = size
        self.__element_size=element_size

    def accesses(self):
        for i in range(self.__size):
            for j in range(self.__size):
                for k in range(self.__size):
                    yield (AccessVerb.LOAD, 0, (i, k), self.__element_size)
                    yield (AccessVerb.LOAD, 1073741824, (k, j), self.__element_size)
                yield (AccessVerb.STORE, 2147483648, (i, j), self.__element_size)


def enumerateOccurances(i):
    c = collections.defaultdict(int)
    r = []

    for x in i:
        r.append((x, c[x]))
        c[x] += 1

    return r


def cxGeneralizedOrderedHelper(ind1, ind2, idx, num):
    e1 = enumerateOccurances(ind1)
    e2 = enumerateOccurances(ind2)

    p = (e2 + e2)[idx : idx + num]

    assert len(p) == num

    i = [x for x in e1[:idx] if x not in p] + p + [x for x in e1[idx:] if x not in p]

    r = [j for (j, _) in i]

    assert collections.Counter(ind1) == collections.Counter(r) and collections.Counter(
        ind2
    ) == collections.Counter(r)

    return r


def cxGeneralizedOrdered(ind1, ind2):
    assert len(ind1) == len(ind2)

    idx = random.randint(0, len(ind1))
    num = random.randint(1, len(ind1) // 2)

    n1 = cxGeneralizedOrderedHelper(ind1[:], ind2[:], idx, num)
    n2 = cxGeneralizedOrderedHelper(ind2[:], ind1[:], idx, num)

    ind1[:] = n1[:]
    ind2[:] = n2[:]

    return (ind1, ind2)


def mutExchangeDifferent(ind):
    size = len(ind)

    i = random.randint(0, size - 1)
    j = i

    while j == i or ind[i] == ind[j]:
        j = random.randint(0, size - 1)

    ind[i], ind[j] = ind[j], ind[i]

    return (ind,)


def simulateMMijk(cache, permutation):
    pass


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

    return [q, q[::-1]]


def getIndex(permutation, *idxs):
    return functools.reduce(lambda a, b: 2 * a | ((idxs[b[0]] >> b[1]) % 2), enumerateOccurances(permutation), 0)


def evalFitness(individual):
    tup = tuple(individual)

    hierarchy = buildCacheSimulator(scoop.shared.getConst('hierarchy'))
    trace = scoop.shared.getConst('trace')

    accesses = 0


    for (v, b, a, s) in trace.accesses():
        accesses += 1

        addr = b + s * getIndex(individual, *a)

        if v == AccessVerb.LOAD:
            hierarchy.load(addr, s)
        elif v == AccessVerb.STORE:
            hierarchy.store(addr, s)

    hierarchy.force_write_back()

    cycles = 0

    for x in hierarchy.levels():
        cycles += x.stats()["HIT_count"] * x.latency

    return (accesses / cycles,)


def parseBits(s):
    return [int(x) for x in s.split(":")]

CACHE = {}

def cachingMap(func, iterable):
    todo = list({tuple(i) for i in iterable if tuple(i) not in CACHE})

    res = scoop.futures.map(func, todo)

    for (i, j) in zip(todo, res):
        CACHE[tuple(i)] = j

    return [CACHE[tuple(i)] for i in iterable]


def buildCacheSimulator(h):
    caches = {}
    memory = cachesim.MainMemory()

    setattr(memory, "latency", h["memory"]["latency"])

    for n, d in h["caches"].items():
        caches[n] = cachesim.Cache(
            n,
            d["sets"],
            d["ways"],
            d["line"],
            replacement_policy=d.get("replacement", "LRU"),
            write_back=d.get("write_back", True),
            write_allocate=d.get("write_allocate", True),
            write_combining=d.get("write_combining", False),
        )

        setattr(caches[n], "latency", d["latency"])

    for n, d in h["caches"].items():
        if "store_to" in d:
            caches[n].set_store_to(caches[d["store_to"]])

        if "load_from" in d:
            caches[n].set_load_from(caches[d["load_from"]])

        if "victims_to" in d:
            caches[n].set_victim_to(caches[d["victims_to"]])


    memory.load_to(caches[h["memory"]["last"]])
    memory.store_from(caches[h["memory"]["last"]])

    return cachesim.CacheSimulator(caches[h["memory"]["first"]], memory)


deap.creator.create("FitnessMax", deap.base.Fitness, weights=(1.0,))
deap.creator.create("Individual", list, fitness=deap.creator.FitnessMax)

toolbox = deap.base.Toolbox()
toolbox.register("evaluate", evalFitness)
toolbox.register("mate", cxGeneralizedOrdered)
toolbox.register("mutate", mutExchangeDifferent)
toolbox.register("select", deap.tools.selBest)
toolbox.register("map", cachingMap)

if __name__ == "__main__":
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
        "-l",
        "--logbook",
        type=pathlib.Path,
        help="output CSV for logbook",
    )
    parser.add_argument(
        "-r",
        "--ranking",
        type=pathlib.Path,
        help="output CSV for final population",
    )
    parser.add_argument(
        "-g",
        "--generations",
        type=int,
        help="number of generations",
        default=10
    )

    args = parser.parse_args()

    with open(args.cache, "r") as f:
        scoop.shared.setConst(hierarchy=yaml.safe_load(f))

    scoop.shared.setConst(trace=TraceMMijk(2**args.bits[0]))

    population = [deap.creator.Individual(x) for x in initialPop(*args.bits)]

    stats = deap.tools.Statistics(key=lambda ind: ind.fitness.values)

    stats.register("avg", numpy.mean)
    stats.register("std", numpy.std)
    stats.register("min", numpy.min)
    stats.register("max", numpy.max)

    pop, logbook = deap.algorithms.eaMuPlusLambda(
        population,
        toolbox,
        40,
        100,
        cxpb=0.3,
        mutpb=0.6,
        ngen=args.generations,
        stats=stats,
        verbose=True,
    )

    ranking = sorted(pop, key=lambda x: x.fitness.values[0], reverse=True)

    if args.logbook is not None:
        with open(args.logbook, "w") as f:
            w = csv.DictWriter(f, ["gen", "nevals", "avg", "std", "min", "max"])

            w.writeheader()

            for l in logbook:
                w.writerow(l)

    if args.ranking is not None:
        with open(args.ranking, "w") as f:
            w = csv.DictWriter(f, ["permutation", "throughput"])

            w.writeheader()

            for r in ranking:
                w.writerow({"permutation": "".join(str(j) for j in r), "throughput": r.fitness.values[0]})

    scoop.logger.info("Processing complete; final ranking:")

    for r, i in enumerate(ranking):
        scoop.logger.info("% 4d % 12.7f %s" % (r, i.fitness.values[0], "".join(str(j) for j in i)))
