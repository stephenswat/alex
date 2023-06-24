import alex.pattern
import alex.schema


def evalFitness(
    individual, hierarchy: alex.schema.CacheHierarchy, pattern: alex.pattern.Pattern
):
    simulator = alex.pattern.runPattern(pattern, hierarchy, individual)

    l1 = simulator._sim.first_level

    cycles = sum(x.stats()["HIT_count"] * x.latency for x in simulator._sim.levels())

    return (l1.backend.STORE_count + l1.backend.LOAD_count) / cycles
