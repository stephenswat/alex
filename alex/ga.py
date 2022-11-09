import random
import time

import numpy.random


class GA:
    def __init__(
        self,
        generations,
        retained_count,
        generated_count,
        elite_count,
        fitness_func,
        crossover_func,
        mutation_func,
        initial_population,
        fitness_func_kwargs=None,
    ):
        self.generations = generations
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

        print(
            f"Generation {n}, size {len(self.population)}, min {min(fitnesses)}, max {max(fitnesses)}, cache size {len(self.fitness_cache)}, runtime {t2 - t1}s"
        )

    def run(self, executor=None):
        for g in range(self.generations - 1):
            self.process_generation(g, executor)

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
                    p=[self.get_fitness(i) ** 2 / total_fitness for i in non_elite_pop],
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

        self.process_generation(self.generations, executor)

    def results(self):
        return [(i, self.get_fitness(i)) for i in self.population]
