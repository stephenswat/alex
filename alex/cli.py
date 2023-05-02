import argparse
import collections
import concurrent.futures
import enum
import hashlib
import logging
import pathlib
import random

import rich.logging
import yaml

import alex.ga
import alex.pattern
import alex.schema
import alex.simulator

log = logging.getLogger(__name__)


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

    return (simulator._sim.first_level.latency * accesses) / cycles


class Trace(str, enum.Enum):
    MMijk = "MMijk"
    MMikj = "MMikj"

    def __str__(self):
        return self.value


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
        type=Trace,
        choices=list(Trace),
        help="trace type to use",
        required=True,
    )
    parser.add_argument(
        "-g", "--generations", type=int, help="number of generations", default=10
    )
    parser.add_argument("-j", "--parallel", type=int, nargs="?", const=-1)
    parser.add_argument(
        "-l", "--log", type=pathlib.Path, help="CSV file to write the log data to"
    )
    parser.add_argument(
        "-r",
        "--ranking",
        type=pathlib.Path,
        help="CSV file to write the species data to",
    )
    parser.add_argument(
        "-v", "--verbose", help="enable verbose output", action="store_true"
    )

    args = parser.parse_args()

    logging.basicConfig(
        level=logging.DEBUG if (args.verbose or False) else logging.INFO,
        format="%(message)s",
        handlers=[
            rich.logging.RichHandler(
                show_path=False, omit_repeated_times=False, markup=True
            )
        ],
    )

    log.info(
        "Access pattern is %s with dimension %s",
        args.trace,
        "x".join(str(i) for i in args.bits),
    )

    log.info("Reading cache configuration from [magenta]%s[/]", args.cache)

    log.info(
        "Cache configuration MD5 sum is [green]%s[/]",
        hashlib.md5(open(args.cache, "rb").read()).hexdigest(),
    )

    with open(args.cache, "r") as f:
        hierarchy = alex.schema.CacheHierarchy(**yaml.safe_load(f))

    genetic_parameters = {
        "retained_count": 20,
        "generated_count": 30,
        "elite_count": 5,
    }

    log.info(
        "Genetic parameters:\n"
        + "\n".join(
            "[yellow]%s[/]: %s" % (str(k), str(v))
            for k, v in genetic_parameters.items()
        )
    )

    ga = alex.ga.GA(
        initial_population=initialPop(*args.bits),
        mutation_func=mutExchangeDifferent,
        crossover_func=cxGeneralizedOrdered,
        fitness_func=evalFitness,
        fitness_func_kwargs={"hierarchy": hierarchy},
        **genetic_parameters,
    )

    log.info("Generation count is %d", args.generations)

    if args.parallel is not None:
        if args.parallel < 0:
            log.info("Running evolution with automatic process count")
        else:
            log.info("Running evolution with %d processes", args.parallel)

        with concurrent.futures.ProcessPoolExecutor(
            max_workers=None if args.parallel < 0 else args.parallel
        ) as executor:
            ga.run(generations=args.generations, executor=executor)
    else:
        log.info("Running evolution sequentially")
        ga.run(generations=args.generations)

    log.info("Evolution complete!")

    log.info(
        "Final population (top 10):\n"
        + "\n".join(
            ",".join(str(x) for x in i) + " : " + str(f)
            for (i, f) in sorted(ga.results(), key=lambda t: t[1], reverse=True)[:10]
        )
    )

    if args.log is not None:
        log.info("Writing full log to %s", args.log)

        with open(args.log, "w") as f:
            ga.write_log(f)

    ranked_cache = sorted(ga.fitness_cache.items(), key=lambda t: t[1], reverse=True)

    log.info(
        "Cache:\n"
        + "\n".join(
            ",".join(str(x) for x in i) + " : " + str(f) for i, f in ranked_cache[:5]
        )
        + "\n...\n"
        + "\n".join(
            ",".join(str(x) for x in i) + " : " + str(f) for i, f in ranked_cache[-5:]
        )
    )

    if args.ranking is not None:
        log.info("Writing full ranking to %s", args.ranking)

        with open(args.ranking, "w") as f:
            ga.write_ranking(f)
