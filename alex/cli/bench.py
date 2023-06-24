import argparse
import concurrent.futures
import csv
import hashlib
import logging
import pathlib

import alex
import alex.logging
import alex.schema

log = logging.getLogger(__name__)


def parseLayout(layout):
    if "," in layout:
        return [int(x) for x in layout.split(",")]
    else:
        return [int(x) for x in layout]


def eval(executor=None):
    pass


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
        "-i",
        "--input",
        type=pathlib.Path,
        help="input CSV file to use",
        required=True,
    )
    parser.add_argument(
        "-j",
        "--parallel",
        type=int,
        nargs="?",
        const=-1,
    )
    parser.add_argument(
        "-v",
        "--verbose",
        help="enable verbose output",
        action="store_true",
    )

    args = parser.parse_args()

    logging.basicConfig(
        level=logging.DEBUG if (args.verbose or False) else logging.INFO,
        format="%(message)s",
        handlers=[alex.logging.LogHandler()],
    )

    log.info("Welcome to ALEX version [bold yellow]%s[/]", alex.__version__)

    log.info("Reading cache configuration from [bold magenta]%s[/]", args.cache)

    log.info(
        "Cache configuration MD5 sum is [bold green]%s[/]",
        hashlib.md5(open(args.cache, "rb").read()).hexdigest(),
    )

    with open(args.cache, "r") as f:
        hierarchy = alex.schema.CacheHierarchy.fromYamlFile(f)

    log.info("Reading input file from [bold magenta]%s[/]", args.input)

    log.info(
        "Input MD5 sum is [bold green]%s[/]",
        hashlib.md5(open(args.input, "rb").read()).hexdigest(),
    )

    individuals = []

    with open(args.input, "r") as f:
        r = csv.DictReader(f)

        for x in r:
            individuals.append(
                alex.schema.BenchmarkInputElement(
                    pattern=x["pattern"], layout=parseLayout(x["layout"])
                )
            )

    log.info("Total number of individuals is [bold cyan]%d[/]", len(individuals))

    log.info("Evaluating fitness function...")

    if args.parallel is not None:
        if args.parallel < 0:
            log.info("Running evaluation with automatic process count")
        else:
            log.info(
                "Running evaluation with [bold yellow]%d[/] processes", args.parallel
            )

        with concurrent.futures.ProcessPoolExecutor(
            max_workers=None if args.parallel < 0 else args.parallel
        ) as executor:
            eval(executor=executor)
    else:
        log.info("Running evaluation sequentially")
        eval()

    log.info("Benchmarking true performance...")
