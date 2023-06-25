import argparse
import csv
import pathlib
import random

import alex.definitions

COMBINATIONS = [
    (alex.definitions.Pattern.MMijk, (9, 9)),
    (alex.definitions.Pattern.MMikj, (9, 9)),
    (alex.definitions.Pattern.MMTijk, (9, 9)),
    (alex.definitions.Pattern.MMTikj, (9, 9)),
    (alex.definitions.Pattern.Jacobi2D, (13, 13)),
    (alex.definitions.Pattern.Himeno, (8, 7, 7)),
    (alex.definitions.Pattern.Cholesky, (10, 10)),
    (alex.definitions.Pattern.Crout, (9, 9)),
]

if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "-o",
        "--output",
        type=pathlib.Path,
        help="CSV file to write to",
        required=True,
    )

    args = parser.parse_args()

    with open(args.output, "w") as f:
        w = csv.DictWriter(f, fieldnames=["pattern", "layout"])

        w.writeheader()

        for p, b in COMBINATIONS:
            for i in range(100):
                lo = [v for v, k in enumerate(b) for _ in range(k)]

                random.shuffle(lo)

                w.writerow({"pattern": str(p), "layout": ",".join(str(x) for x in lo)})
