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

import deap.creator
import deap.base
import deap.tools
import deap.algorithms

logging.basicConfig(level=logging.DEBUG)


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


def initial_pop(*mtpl):
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


def eval(root, individual):
    name = "".join(string.ascii_lowercase[x] for x in individual)
    dirname = root / name

    if not os.path.isdir(dirname):
        os.mkdir(dirname)

    if not os.path.isfile(dirname / "run"):
        with open(dirname / "output.txt", "w") as f:
            subprocess.run(
                [
                    os.environ.get("CXX", "c++"),
                    "-O2",
                    "-march=x86-64-v3",
                    "-mtune=generic",
                    "-std=c++17",
                    "-DNDEBUG",
                    "-DPERMUTATION=%s" % ",".join(str(x) for x in individual),
                    "-o",
                    dirname / "run",
                    pathlib.Path(os.path.dirname(os.path.realpath(__file__)))
                    / "benchmark"
                    / "main.cpp",
                ],
                check=True,
                stdout=f,
                stderr=f,
            )

    p = subprocess.run(
        [
            dirname / "run",
        ],
        check=True,
        capture_output=True,
    )

    t = float(p.stdout)

    return (t,)


if __name__ == "__main__" or True:
    output_dir = pathlib.Path(tempfile.mkdtemp())

    logging.info("Using temporary directory {}".format(output_dir))

    deap.creator.create("FitnessMax", deap.base.Fitness, weights=(1.0,))
    deap.creator.create("Individual", list, fitness=deap.creator.FitnessMax)

    toolbox = deap.base.Toolbox()

    toolbox.register("evaluate", lambda x: eval(output_dir, x))
    toolbox.register("mate", cxGeneralizedOrdered)
    toolbox.register("mutate", deap.tools.mutShuffleIndexes, indpb=0.2)
    toolbox.register("select", deap.tools.selTournament, tournsize=3)

    population = [deap.creator.Individual(x) for x in initial_pop(8, 8)]

    stats = deap.tools.Statistics(key=lambda ind: ind.fitness.values)

    stats.register("avg", numpy.mean)
    stats.register("std", numpy.std)
    stats.register("min", numpy.min)
    stats.register("max", numpy.max)

    pop, logbook = deap.algorithms.eaMuPlusLambda(
        population,
        toolbox,
        100,
        50,
        cxpb=0.5,
        mutpb=0.2,
        ngen=40,
        stats=stats,
        verbose=True,
    )

    print(pop)
