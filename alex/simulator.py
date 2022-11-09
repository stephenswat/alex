import cachesim

import alex.schema


class CacheSimulator:
    def __init__(self, hierarchy: alex.schema.CacheHierarchy):
        caches = {}
        memory = cachesim.MainMemory()

        setattr(memory, "latency", hierarchy.memory.latency)

        for n, d in hierarchy.caches.items():
            caches[n] = cachesim.Cache(
                n,
                d.sets,
                d.ways,
                d.line,
                replacement_policy=d.replacement or alex.schema.ReplacementPolicy.LRU,
                write_back=d.write_back,
                write_allocate=d.write_allocate,
                write_combining=d.write_combining,
            )

            setattr(caches[n], "latency", d.latency)

        for n, d in hierarchy.caches.items():
            if d.store_to is not None:
                caches[n].set_store_to(caches[d.store_to])

            if d.load_from is not None:
                caches[n].set_load_from(caches[d.load_from])

            if d.victims_to is not None:
                caches[n].set_victim_to(caches[d.victims_to])

        memory.load_to(caches[hierarchy.memory.last])
        memory.store_from(caches[hierarchy.memory.last])

        self._sim = cachesim.CacheSimulator(caches[hierarchy.memory.first], memory)
