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


def render_pattern(ptrn: str):
    splt = ptrn.split("_")

    if splt[0] in ["Cholesky", "Crout"] or splt[0][:2] == "MM":
        if splt[0][:3] == "MMT":
            rem = str(splt[1]) + ", " + str(splt[1])
        else:
            rem = str(splt[1])
    else:
        rem = ", ".join(str(i) for i in splt[1:])

    return f"$\\textsc{{{splt[0]}}}({rem}; 4)$"


palette = ["#d62728", "#1f77b4"]


def make_evolution_plot(path: pathlib.Path):
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
            ax.set_title(render_pattern(f"{t}_{s}"))
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
        "fitness_evolution.pdf", bbox_inches="tight", pad_inches=0.02
    )


def make_violin_plot(path: pathlib.Path):
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
        [render_pattern(f"{t}_{s}") for (t, s) in uniques],
        rotation=30,
        ha="right",
        rotation_mode="anchor",
    )

    matplotlib.pyplot.savefig(
        "fitness_violin.pdf", bbox_inches="tight", pad_inches=0.02
    )


if __name__ == "__main__":
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

    make_evolution_plot(args.input)
    make_violin_plot(args.input)
