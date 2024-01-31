import argparse
import pathlib
import re

import matplotlib.patches
import matplotlib.pyplot
import numpy
import pandas

ORDER = [
    "MMijk",
    "MMTijk",
    "MMikj",
    "MMTikj",
    "Jacobi2D",
    "Cholesky",
    "Crout",
    "Himeno",
]


def parse_filename(s: str):
    if m := re.fullmatch(
        r"([A-Za-z0-9]+)-(\d+(?:_\d+)*)-(\d+)-([A-Za-z0-9_\-]+)-(?:log|ranking).csv", s
    ):
        return (m.group(1), m.group(2), m.group(3), m.group(4))
    else:
        raise ValueError("Invalid file name " + s + "!")


def render_pattern(ptrn: str, tex: bool = True):
    splt = ptrn.split("_")

    if splt[0] in ["Cholesky", "Crout"] or splt[0][:2] == "MM":
        if splt[0][:3] == "MMT":
            rem = str(splt[1]) + ", " + str(splt[1])
        else:
            rem = str(splt[1])
    else:
        rem = ", ".join(str(i) for i in splt[1:])

    return f"$\\textsc{{{splt[0]}}}({rem}; 4)$" if tex else f"{splt[0]}({rem}; 4)"


palette = ["#d62728", "#1f77b4"]


def make_evolution_plot(path: pathlib.Path, output: pathlib.Path, tex: bool = True):
    log_glob = path.glob("*-log.csv")

    inputs = [parse_filename(i.name) for i in log_glob]

    uniques = sorted(
        list(set((j[0], j[1]) for j in inputs)), key=lambda x: ORDER.index(x[0])
    )
    processors = sorted(list(set(i[3] for i in inputs)))

    fig, axs = matplotlib.pyplot.subplots(
        figsize=(3.333, 3),
        nrows=int(len(uniques) / 2 + 0.5),
        ncols=2,
        constrained_layout=True,
        sharex=True,
    )

    fig.supxlabel("Generation")
    fig.supylabel("Fitness")

    for (t, s), (x, y) in zip(uniques, numpy.ndindex(axs.shape)):
        for i, p in enumerate(processors):
            df_l = pandas.read_csv(path / f"{t}-{s}-0-{p}-log.csv")

            ax = axs[x, y]
            ax.set_title(render_pattern(f"{t}_{s}", tex))
            ax.plot(
                df_l["generation"],
                df_l["mean_fitness"],
                "--",
                color=palette[i],
                linewidth=0.5,
            )
            ax.plot(
                df_l["generation"],
                df_l["max_fitness"],
                color=palette[i],
                linewidth=0.5,
            )
            ax.plot(
                df_l["generation"],
                df_l["min_fitness"],
                color=palette[i],
                linewidth=0.5,
            )
            ax.fill_between(
                df_l["generation"],
                df_l["min_fitness"],
                df_l["max_fitness"],
                alpha=0.2,
                color=palette[i],
            )

    matplotlib.pyplot.savefig(
        output,
        bbox_inches="tight",
        pad_inches=0.02,
    )


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
        "-o",
        "--output",
        type=pathlib.Path,
        help="output PDF file",
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
            "figure.titlesize": 8,
            "axes.titlesize": 8,
            "figure.labelsize": "medium",
            "font.size": 8,
            "font.family": "serif",
            "text.usetex": args.use_tex,
            "text.latex.preamble": """
            \\usepackage{libertine}
            \\usepackage[libertine]{newtxmath}
            """,
        }
    )

    make_evolution_plot(args.input, args.output, args.use_tex)
