import argparse
import pathlib
import re

import matplotlib.patches
import matplotlib.pyplot
import numpy
import pandas

from common import parse_filename, render_pattern

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


palette = ["#d62728", "#1f77b4"]


def make_violin_plot(path: pathlib.Path, output: pathlib.Path, tex: bool = True):
    rnk_glob = path.glob("*-ranking.csv")

    inputs = [parse_filename(i.name) for i in rnk_glob]

    fig, ax = matplotlib.pyplot.subplots(figsize=(3.333, 2), constrained_layout=True)

    ax.set_ylabel("Fitness")
    ax.set_xlabel("Access Pattern")

    uniques = sorted(
        list(set((j[0], j[1]) for j in inputs)), key=lambda x: ORDER.index(x[0])
    )
    pos = list(range(len(uniques)))

    labels = []

    for i, c in enumerate(sorted(list(set(i[3] for i in inputs)))):
        labels.append(
            (matplotlib.patches.Patch(color=palette[i], alpha=0.8), c.replace("_", " "))
        )

        dfs_r = []

        for t, s in uniques:
            dft_r = pandas.read_csv(path / f"{t}-{s}-0-{c}-ranking.csv")
            dft_r["pattern"] = t
            dft_r["size"] = s
            dfs_r.append(dft_r)

        df_r = pandas.concat(dfs_r, axis=0, ignore_index=True)

        parts = ax.violinplot(
            [
                df_r[(df_r["pattern"] == t) & (df_r["size"] == s)]["fitness"]
                for (t, s) in uniques
            ],
            pos,
            showextrema=False,
            widths=0.9,
        )

        for pc in parts["bodies"]:
            pc.set_facecolor(palette[i])
            pc.set_alpha(0.8)

    ax.legend(*zip(*labels))
    ax.set_xticks(pos)
    ax.set_xticklabels(
        [render_pattern(f"{t}_{s}", tex) for (t, s) in uniques],
        rotation=30,
        ha="right",
        rotation_mode="anchor",
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

    make_violin_plot(args.input, args.output, args.use_tex)
