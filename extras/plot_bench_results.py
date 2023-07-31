import matplotlib.pyplot
import numpy
import pandas
import scipy

if __name__ == "__main__":
    df = pandas.read_csv("bench.csv")

    df_cv = df["runtime_dev"] / df["runtime"]

    print(f"The maximum CV value is {df_cv.max()}")

    matplotlib.rcParams.update(
        {
            "font.size": 8,
            "font.family": "serif",
            "text.usetex": True,
            "text.latex.preamble": """
            \\usepackage{libertine}
            \\usepackage[libertine]{newtxmath}
            """,
        }
    )

    fig, ax = matplotlib.pyplot.subplots(figsize=(3.333, 2.5), constrained_layout=True)

    ax.set_ylabel("Runtime [ms]")
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

        corr = numpy.corrcoef(dfs[["fitness", "runtime"]], rowvar=False)[0, 1]

        spear = scipy.stats.spearmanr(dfs[["fitness", "runtime"]])

        print(f"ρP for {p} is {corr}, ρS is {spear.statistic}")

        ax.scatter(
            dfs["fitness"],
            dfs["runtime"] / 1000000,
            s=2,
            label=f"\\textsc{{{p}}}",
        )

    lgnd = ax.legend()
    for handle in lgnd.legend_handles:
        handle.set_sizes([12.0])
    fig.savefig("fitness_vs_runtime.pdf", bbox_inches="tight", pad_inches=0.02)
