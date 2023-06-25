import argparse
import pathlib

import matplotlib.pyplot
import pandas


def render_pattern(ptrn: str):
    splt = ptrn.split("_")

    args = ", ".join("2^{{{}}}".format(i) for i in splt[1:])

    return f"{splt[0]}"


def main() -> None:
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
        "Cholesky_12_12",
        "Crout_12_12",
        "Himeno_10_9_9",
        "Jacobi2D_15_15",
        "MMijk_11_11",
        "MMikj_11_11",
        "MMTijk_11_11",
        "MMTikj_11_11",
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

    fig, ax = matplotlib.pyplot.subplots()

    ax.set_ylabel("Fitness")
    ax.set_xlabel("Generation")

    for t in ptrns:
        rdf = df_l[df_l["pattern"] == t]
        ax.plot(rdf["generation"], rdf["max_fitness"], label=t)

    fig.legend()

    matplotlib.pyplot.show()

    fig, ax = matplotlib.pyplot.subplots(layout="constrained", figsize=(3.5, 2))

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

    matplotlib.pyplot.savefig("destination_path.eps", format="eps")


if __name__ == "__main__":
    main()
