import collections
import csv
import logging
import random
import time

import numpy
import numpy.random

import alex.signal

log = logging.getLogger(__name__)


GenerationRecord = collections.namedtuple(
    "GenerationRecord",
    [
        "generation",
        "size",
        "min_fitness",
        "max_fitness",
        "mean_fitness",
        "dev_fitness",
        "species_size",
        "runtime",
    ],
)


class GA:
    def __init__(
        self,
        retained_count,
        generated_count,
        elite_count,
        fitness_func,
        crossover_func,
        mutation_func,
        initial_population,
        fitness_func_kwargs=None,
    ):
        self.generation = 0
        self.retained_count = retained_count
        self.generated_count = generated_count
        self.elite_count = elite_count
        self.fitness_cache = {}
        self.fitness_func = fitness_func
        self.fitness_func_kwargs = fitness_func_kwargs or dict()
        self.crossover_func = crossover_func
        self.mutation_func = mutation_func
        self.generation_log = []

        self.population = initial_population

    def get_fitness(self, i):
        if i not in self.fitness_cache:
            self.fitness_cache[i] = self.fitness_func(i, **self.fitness_func_kwargs)

        return self.fitness_cache[i]

    def resolve_population_fitness(self, executor):
        todo = [x for x in self.population if x not in self.fitness_cache]

        if executor is None:
            results = map(
                lambda i: self.fitness_func(i, **self.fitness_func_kwargs), todo
            )
        else:
            futures = [
                executor.submit(self.fitness_func, i, **self.fitness_func_kwargs)
                for i in todo
            ]
            results = [f.result() for f in futures]

        for i, f in zip(todo, results):
            self.fitness_cache[i] = f

    def process_generation(self, n, executor):
        t1 = time.perf_counter()
        self.resolve_population_fitness(executor)
        t2 = time.perf_counter()

        fitnesses = [self.get_fitness(x) for x in self.population]

        dlt = self.generation > 0

        size = len(self.population)

        self.generation_log.append(
            GenerationRecord(
                generation=self.generation,
                size=size,
                min_fitness=numpy.min(fitnesses),
                max_fitness=numpy.max(fitnesses),
                mean_fitness=numpy.mean(fitnesses),
                dev_fitness=numpy.std(fitnesses),
                species_size=len(self.fitness_cache),
                runtime=t2 - t1,
            )
        )

        tg = self.generation_log[-1]
        if dlt:
            lg = self.generation_log[-2]

        dlt_size = tg.size - lg.size if dlt else tg.size
        dlt_min = tg.min_fitness - lg.min_fitness if dlt else tg.min_fitness
        dlt_max = tg.max_fitness - lg.max_fitness if dlt else tg.max_fitness
        dlt_spc = tg.species_size - lg.species_size if dlt else tg.species_size

        log.info(
            f"Generation [bold cyan]{n:5d}[/], "
            + f"size [bold cyan]{tg.size:5d}[/]"
            + f" ([bold cyan]{dlt_size:+3d}[/])"
            + ", "
            + f"min [bold cyan]{tg.min_fitness:8.6f}[/]"
            + f" ([bold cyan]{dlt_min:+9.6f}[/])"
            + ", "
            + f"max [bold cyan]{tg.max_fitness:8.6f}[/]"
            + f" ([bold cyan]{dlt_max:+9.6f}[/])"
            + ", "
            + f"records [bold cyan]{tg.species_size:6d}[/]"
            + f" ([bold cyan]{dlt_spc:+3d}[/])"
            + ", "
            + f"runtime [bold cyan]{t2 - t1:7.3f}[/] sec",
            extra={"highlight": False},
        )

    def run(self, generations=1, executor=None):
        with alex.signal.CatchSigInt() as s:
            for _ in range(generations - 1):
                self.process_generation(self.generation, executor)

                if not s.valid():
                    log.warning("Stopping evolutionary process due to interrupt")
                    break

                tmp_pop = sorted(
                    list(set(self.population)),
                    key=lambda x: self.get_fitness(x),
                    reverse=True,
                )

                elite_pop = tmp_pop[: self.elite_count]
                non_elite_pop = tmp_pop[self.elite_count :]

                non_elite_size = self.retained_count - self.elite_count

                if non_elite_size > 0 and len(non_elite_pop) > 0:
                    total_fitness = sum(self.get_fitness(i) for i in non_elite_pop)
                    non_elite_selection = numpy.random.choice(
                        len(non_elite_pop),
                        size=min(non_elite_size, len(non_elite_pop)),
                        replace=False,
                        p=[self.get_fitness(i) / total_fitness for i in non_elite_pop],
                    )
                else:
                    non_elite_selection = []

                mu = elite_pop + [non_elite_pop[i] for i in non_elite_selection]

                lam = [
                    self.mutation_func(random.choice(mu))
                    if random.random() < 0.5
                    else self.crossover_func(*random.sample(mu, k=2))
                    for _ in range(self.generated_count)
                ]

                self.population = mu + lam

                self.generation += 1
            else:
                self.process_generation(self.generation, executor)

    def results(self):
        return [(i, self.get_fitness(i)) for i in self.population]

    def write_log(self, file):
        writer = csv.DictWriter(
            file,
            fieldnames=[
                "generation",
                "size",
                "min_fitness",
                "max_fitness",
                "mean_fitness",
                "dev_fitness",
                "species_size",
                "runtime",
            ],
        )
        writer.writeheader()

        for i in self.generation_log:
            writer.writerow(i._asdict())

    def write_ranking(self, file):
        writer = csv.DictWriter(file, fieldnames=["individual", "fitness"])
        writer.writeheader()

        for i, v in sorted(
            self.fitness_cache.items(), key=lambda x: x[1], reverse=True
        ):
            writer.writerow({"individual": ",".join(str(x) for x in i), "fitness": v})
