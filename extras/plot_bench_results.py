import argparse
import collections
import pathlib

import matplotlib.pyplot
import numpy
import pandas
import scipy

if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "-i",
        "--input",
        help="input directory files (model:file)",
        nargs="+",
        action="extend",
        required=True,
    )
    parser.add_argument(
        "-o",
        "--output",
        help="output PDF file",
        type=pathlib.Path,
        required=True,
    )
    parser.add_argument(
        "--no-tex",
        help="disable TeX rendering",
        action="store_false",
        dest="use_tex",
    )

    args = parser.parse_args()

    matplotlib.rcParams.update(
        {
            "figure.labelsize": "medium",
            "figure.titlesize": "medium",
            "axes.labelsize": "medium",
            "axes.titlesize": "medium",
            "font.size": 8,
            "font.family": "serif",
            "text.usetex": args.use_tex,
            "text.latex.preamble": """
            \\usepackage{libertine}
            \\usepackage[libertine]{newtxmath}
            """,
        }
    )

    fig, axs = matplotlib.pyplot.subplots(
        figsize=(3.333, 1.5 * len(args.input)),
        nrows=len(args.input),
        ncols=1,
        constrained_layout=True,
        sharex=True,
    )

    for (n, s), ax in zip(
        enumerate(args.input), axs.flat if len(args.input) > 1 else [axs]
    ):
        try:
            processor, file_name = s.split(":")
        except:
            raise ValueError(
                'Input "%s" could not be parsed as [CPU NAME]:[FILE] pair' % s
            )

        print("CPU model: %s" % processor.replace("_", " "))

        df = pandas.read_csv(file_name)

        df_cv = df["runtime_dev"] / df["runtime"]

        print(f"The maximum CV value is {df_cv.max()}")

        ax.set_title(processor.replace("_", " "))
        ax.set_ylabel("Runtime [ms]")

        if n == len(args.input) - 1:
            ax.set_xlabel("Fitness")

        for p in [
            "MMijk",
            "MMTijk",
            "MMikj",
            "MMTikj",
            "Jacobi2D",
            "Cholesky",
            "Crout",
            "Himeno",
        ]:
            dfs = df[df["pattern"] == p]

            layout = dfs["layout"].iloc[0]

            counter = collections.Counter([int(x) for x in layout.split(",")])

            bits = [counter.get(x) for x in range(max(counter.keys()) + 1)]

            corr = numpy.corrcoef(dfs[["fitness", "runtime"]], rowvar=False)[0, 1]

            spear = scipy.stats.spearmanr(dfs[["fitness", "runtime"]])

            print(f"ρP for {p} is {corr}, ρS is {spear.statistic}")

            if p in ["Cholesky", "Crout"] or p[:2] == "MM":
                if p[:3] == "MMT":
                    bit_suffix = str(bits[0]) + ", " + str(bits[0])
                else:
                    bit_suffix = str(bits[0])
            else:
                bit_suffix = ",".join(str(x) for x in bits)

            ax.scatter(
                dfs["fitness"],
                dfs["runtime"] / 1000000,
                s=2,
                label=f"$\\textsc{{{p}}}({bit_suffix}; 4)$"
                if args.use_tex
                else f"{p}({bit_suffix}; 4)"
                if args.use_tex
                else f"{p}({bit_suffix}; 4)",
            )

        if n == 0:
            lgnd = ax.legend(
                ncol=2, handletextpad=0.2, columnspacing=0.5, handlelength=1
            )
            for handle in lgnd.legend_handles:
                handle.set_sizes([10.0])

        if n != len(args.input) - 1:
            print()

    fig.savefig(args.output, bbox_inches="tight", pad_inches=0.02)
