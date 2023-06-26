import matplotlib.pyplot
import pandas

if __name__ == "__main__":
    df = pandas.read_csv("bench.csv")

    matplotlib.pyplot.ylabel("Runtime [ms]")
    matplotlib.pyplot.xlabel("Fitness")
    matplotlib.pyplot.gcf().set_size_inches(3.5, 3.75)
    # matplotlib.pyplot.yscale("log")
    # matplotlib.pyplot.xscale("log")

    for p in ["MMTijk", "Jacobi2D", "Himeno", "Cholesky"]:
        dfs = df[df["pattern"] == p]

        matplotlib.pyplot.errorbar(
            dfs["fitness"],
            dfs["runtime"] / 1000000,
            yerr=dfs["runtime_dev"] / 1000000,
            fmt=".",
            label=p,
        )

    matplotlib.pyplot.legend()
    matplotlib.pyplot.tight_layout()
    matplotlib.pyplot.savefig("fitness_vs_runtime.pdf")
