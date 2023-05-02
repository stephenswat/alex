import csv
import logging
import random
import time

import numpy.random

import alex.signal

log = logging.getLogger(__name__)


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

        log.info(
            f"Generation {n}, size {len(self.population)}, min {min(fitnesses)}, "
            + f"max {max(fitnesses)}, cache size {len(self.fitness_cache)}, "
            + f"runtime {t2 - t1} sec"
        )

    def run(self, generations=1, executor=None):
        with alex.signal.CatchSigInt() as s:
            while self.generation < generations:
                self.process_generation(self.generation, executor)

                if not s.valid():
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
                    total_fitness = sum(self.get_fitness(i) ** 2 for i in non_elite_pop)
                    non_elite_selection = numpy.random.choice(
                        len(non_elite_pop),
                        size=min(non_elite_size, len(non_elite_pop)),
                        replace=False,
                        p=[
                            self.get_fitness(i) ** 2 / total_fitness
                            for i in non_elite_pop
                        ],
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

    def write_ranking(self, file):
        writer = csv.DictWriter(file, fieldnames=["individual", "fitness"])
        writer.writeheader()
