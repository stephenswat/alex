import argparse
import collections
import concurrent.futures
import hashlib
import logging
import math
import pathlib
import random

import alex
import alex.cli.utils
import alex.definitions
import alex.fitness
import alex.ga
import alex.logging
import alex.pattern
import alex.schema
import alex.simulator
import alex.utils

log = logging.getLogger(__name__)


def cxGeneralizedOrdered(ind1, ind2):
    idx = random.randint(0, len(ind1))
    num = random.randint(1, len(ind1) // 2)

    e1 = alex.utils.enumerateOccurances(ind1)
    e2 = alex.utils.enumerateOccurances(ind2)

    p = (e2 + e2)[idx : idx + num]

    assert len(p) == num

    i = [x for x in e1[:idx] if x not in p] + p + [x for x in e1[idx:] if x not in p]

    r = [j for (j, _) in i]

    assert collections.Counter(ind1) == collections.Counter(r) and collections.Counter(
        ind2
    ) == collections.Counter(r)

    nind = tuple(r)

    return nind


def rotateHelper(lst, n):
    return lst[n:] + lst[:n]


def mutExchangeDifferent(ind):
    size = len(ind)

    i = random.randint(0, size - 3)
    j = random.randint(i + 1, size - 1)

    nind = tuple(ind[:i] + rotateHelper(ind[i:j], 1) + ind[j:])

    # assert tuple(nind) != ind

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

    # return [tuple(random.sample(q, k=len(q))) for _ in range(15)]


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
        type=alex.cli.utils.parseBits,
        help="colon-separated bit counts",
        required=True,
    )
    parser.add_argument(
        "-t",
        "--pattern",
        type=alex.definitions.Pattern,
        choices=list(alex.definitions.Pattern),
        help="pattern type to use",
        required=True,
    )
    parser.add_argument(
        "-g",
        "--generations",
        type=int,
        help="number of generations",
        default=10,
    )
    parser.add_argument(
        "-j",
        "--parallel",
        type=int,
        nargs="?",
        const=-1,
    )
    parser.add_argument(
        "-l",
        "--log",
        type=pathlib.Path,
        help="CSV file to write the log data to",
    )
    parser.add_argument(
        "-r",
        "--ranking",
        type=pathlib.Path,
        help="CSV file to write the species data to",
    )
    parser.add_argument(
        "-v",
        "--verbose",
        help="enable verbose output",
        action="store_true",
    )

    args = parser.parse_args()

    assert args.generations > 0

    logging.basicConfig(
        level=logging.DEBUG if (args.verbose or False) else logging.INFO,
        format="%(message)s",
        handlers=[alex.logging.LogHandler()],
    )

    log.info("Welcome to ALEX version [bold yellow]%s[/]", alex.__version__)

    log.info(
        "Access pattern is [bold yellow]%s[/] with dimension [bold yellow]%s[/]",
        args.pattern,
        ":".join(str(i) for i in args.bits),
    )

    log.info("Reading cache configuration from [bold magenta]%s[/]", args.cache)

    log.info(
        "Cache configuration MD5 sum is [bold green]%s[/]",
        hashlib.md5(open(args.cache, "rb").read()).hexdigest(),
    )

    with open(args.cache, "r") as f:
        hierarchy = alex.schema.CacheHierarchy.fromYamlFile(f)

    genetic_parameters = {
        "retained_count": 20,
        "generated_count": 20,
    }

    log.info(
        "Genetic parameters: "
        + ", ".join(
            "[yellow]%s[/]: %s" % (str(k), str(v))
            for k, v in genetic_parameters.items()
        )
    )

    ga = alex.ga.GA(
        initial_population=initialPop(*args.bits),
        mutation_func=mutExchangeDifferent,
        crossover_func=cxGeneralizedOrdered,
        fitness_func=alex.fitness.evalFitness,
        fitness_func_kwargs={"hierarchy": hierarchy, "pattern": args.pattern},
        **genetic_parameters,
    )

    log.info("Generation count is [bold yellow]%d[/]", args.generations)

    log.info(
        "Total solution space has size [bold cyan]%d[/]",
        math.factorial(sum(args.bits))
        / math.prod(math.factorial(i) for i in args.bits),
    )

    if args.parallel is not None:
        if args.parallel < 0:
            log.info("Running evolution with automatic process count")
        else:
            log.info(
                "Running evolution with [bold yellow]%d[/] processes", args.parallel
            )

        with concurrent.futures.ProcessPoolExecutor(
            max_workers=None if args.parallel < 0 else args.parallel
        ) as executor:
            ga.run(generations=args.generations, executor=executor)
    else:
        log.info("Running evolution sequentially")
        ga.run(generations=args.generations)

    log.info("Evolution complete!")

    ranked_results = sorted(ga.results(), key=lambda t: t[1], reverse=True)

    log.info(
        f"Final population contains [bold cyan]{len(ranked_results)}[/] individuals"
    )

    log.info(
        f"Fittest is [bold blue]{','.join(str(i) for i in ranked_results[0][0])}[/] "
        + f"([bold cyan]{ranked_results[0][1]}[/])"
    )

    if args.log is not None:
        log.info("Writing full log to [bold magenta]%s[/]", args.log)

        with open(args.log, "w") as f:
            ga.write_log(f)

    ranked_cache = sorted(ga.fitness_cache.items(), key=lambda t: t[1], reverse=True)

    log.info(
        f"Species contains a total of [bold cyan]{len(ranked_cache)}[/] individuals"
    )

    if args.ranking is not None:
        log.info("Writing full ranking to [bold magenta]%s[/]", args.ranking)

        with open(args.ranking, "w") as f:
            ga.write_ranking(f)
