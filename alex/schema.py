import enum

import pydantic


class ReplacementPolicy(str, enum.Enum):
    LRU = "LRU"


class MainMemory(pydantic.BaseModel):
    first: str
    last: str
    latency: int


class Cache(pydantic.BaseModel):
    sets: int
    ways: int
    line: int
    replacement: ReplacementPolicy
    write_back: bool = True
    write_allocate: bool = True
    write_combining: bool = False
    store_to: str | None
    load_from: str | None
    victims_to: str | None
    latency: int


class CacheHierarchy(pydantic.BaseModel):
    caches: dict[str, Cache]
    memory: MainMemory
