import argparse
import pathlib
import re
import csv

import matplotlib.patches
import matplotlib.pyplot
import numpy
import pandas


from common import parse_filename


def is_canonical(s: str):
    a = [int(x) for x in s.split(",")]
    return a == sorted(a) or a == sorted(a, reverse=True)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "-i",
        "--input",
        type=pathlib.Path,
        help="input directory",
        required=True,
    )
    parser.add_argument(
        "-c",
        "--cpu",
        type=str,
        help="CPU model",
        required=True,
    )
    parser.add_argument(
        "-o",
        "--output",
        type=pathlib.Path,
        help="output CSV file",
        required=True,
    )

    args = parser.parse_args()

    rnk_glob = args.input.glob("*-ranking.csv")

    inputs = [
        (c, i)
        for i in rnk_glob
        if (c := parse_filename(i.name))[3] == args.cpu and c[2] == "0"
    ]

    with open(args.output, "w") as of:
        ow = csv.DictWriter(of, fieldnames=["pattern", "layout"])
        ow.writeheader()

        for c, f in inputs:
            with open(f, "r") as fp:
                r = csv.DictReader(fp)
                rows = [x for x in r]
                if is_canonical(rows[0]["individual"]):
                    continue
                out = [rows[0]["individual"]] + [
                    x["individual"] for x in rows if is_canonical(x["individual"])
                ]
                for o in out:
                    ow.writerow(
                        {
                            "pattern": c[0],
                            "layout": o,
                        }
                    )
