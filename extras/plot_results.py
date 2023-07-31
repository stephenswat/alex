import argparse
import pathlib

import matplotlib.pyplot
import numpy
import pandas


def render_pattern(ptrn: str):
    splt = ptrn.split("_")

    rem = ", ".join(str(i) for i in splt[1:])

    return f"$\\textsc{{{splt[0]}}}({rem})$"


def main() -> None:
    matplotlib.rcParams.update(
        {
            "figure.titlesize": 8,
            "axes.titlesize": 8,
            "figure.labelsize": "medium",
            "font.size": 8,
            "font.family": "serif",
            "text.usetex": True,
            "text.latex.preamble": """
            \\usepackage{libertine}
            \\usepackage[libertine]{newtxmath}
            """,
        }
    )

    parser = argparse.ArgumentParser()

    parser.add_argument(
        "-i",
        "--input",
        type=pathlib.Path,
        help="input directory",
        required=True,
    )

    args = parser.parse_args()

    dfs_l = []
    dfs_r = []

    ptrns = [
        "MMijk_11_11",
        "MMTijk_11_11",
        "MMikj_11_11",
        "MMTikj_11_11",
        "Jacobi2D_15_15",
        "Cholesky_12_12",
        "Crout_12_12",
        "Himeno_10_9_9",
    ]

    for t in ptrns:
        dft_l = pandas.read_csv(args.input / f"{t}_log.csv")
        dft_l["pattern"] = t
        dfs_l.append(dft_l)

        dft_r = pandas.read_csv(args.input / f"{t}_ranking.csv")
        dft_r["pattern"] = t
        dfs_r.append(dft_r)

    df_l = pandas.concat(dfs_l, axis=0, ignore_index=True)
    df_r = pandas.concat(dfs_r, axis=0, ignore_index=True)

    matplotlib.rc("font", **{"size": 8})

    fig, axs = matplotlib.pyplot.subplots(
        figsize=(3.333, 3.5), nrows=4, ncols=2, constrained_layout=True, sharex=True
    )

    fig.supxlabel("Generation")
    fig.supylabel("Fitness")

    for t, (x, y) in zip(ptrns, numpy.ndindex(axs.shape)):
        ax = axs[x, y]
        rdf = df_l[df_l["pattern"] == t]
        ax.set_title(render_pattern(t))
        ax.plot(
            rdf["generation"],
            rdf["mean_fitness"],
            "--",
            label=render_pattern(t),
            color="black",
            linewidth=0.5,
        )
        ax.plot(
            rdf["generation"],
            rdf["max_fitness"],
            label=render_pattern(t),
            color="black",
            linewidth=0.5,
        )
        ax.plot(
            rdf["generation"],
            rdf["min_fitness"],
            label=render_pattern(t),
            color="black",
            linewidth=0.5,
        )
        ax.fill_between(
            rdf["generation"],
            rdf["min_fitness"],
            rdf["max_fitness"],
            alpha=0.2,
            color="#D43F3A",
        )

    matplotlib.pyplot.savefig(
        "fitness_evolution.pdf", bbox_inches="tight", pad_inches=0.02
    )

    fig, ax = matplotlib.pyplot.subplots(figsize=(3.333, 2.5), constrained_layout=True)

    ax.set_ylabel("Fitness")
    ax.set_xlabel("Access Pattern")

    pos = list(range(len(ptrns)))

    parts = ax.violinplot(
        [df_r[df_r["pattern"] == t]["fitness"] for t in ptrns],
        pos,
        showextrema=False,
        widths=0.9,
    )

    for pc in parts["bodies"]:
        pc.set_facecolor("#D43F3A")
        pc.set_edgecolor("black")
        pc.set_alpha(1)

    ax.vlines(
        [i + 0.0012 for i in pos],
        [
            df_l[(df_l["pattern"] == t) & (df_l["generation"] == 0)][
                "min_fitness"
            ].min()
            for t in ptrns
        ],
        [
            df_l[(df_l["pattern"] == t) & (df_l["generation"] == 0)][
                "max_fitness"
            ].max()
            for t in ptrns
        ],
        color="k",
        linestyle="-",
        lw=2,
        label="Initial population",
    )

    ax.hlines(
        [
            df_l[(df_l["pattern"] == t) & (df_l["generation"] == 0)][
                "min_fitness"
            ].min()
            for t in ptrns
        ]
        + [
            df_l[(df_l["pattern"] == t) & (df_l["generation"] == 0)][
                "max_fitness"
            ].max()
            for t in ptrns
        ],
        [i - 0.1 for i in pos] * 2,
        [i + 0.1 for i in pos] * 2,
        color="k",
        linestyle="-",
        lw=1,
    )

    ax.vlines(
        pos,
        [df_r[df_r["pattern"] == t]["fitness"].min() for t in ptrns],
        [df_r[df_r["pattern"] == t]["fitness"].max() for t in ptrns],
        color="k",
        linestyle="-",
        lw=0.5,
    )

    ax.set_xticks(pos)
    ax.set_xticklabels([render_pattern(i) for i in ptrns], rotation=45, ha="right")

    matplotlib.pyplot.savefig(
        "fitness_violin.pdf", bbox_inches="tight", pad_inches=0.02
    )


if __name__ == "__main__":
    main()
