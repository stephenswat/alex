import enum
import typing

import pydantic
import yaml

import alex.definitions


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
    store_to: typing.Optional[str]
    load_from: typing.Optional[str]
    victims_to: typing.Optional[str]
    latency: int


class CacheHierarchy(pydantic.BaseModel):
    caches: dict[str, Cache]
    memory: MainMemory

    @staticmethod
    def fromYamlFile(f):
        return CacheHierarchy(**yaml.safe_load(f))


class BenchmarkInputElement(pydantic.BaseModel):
    pattern: alex.definitions.Pattern
    layout: typing.List[int]


class BenchmarkInput(pydantic.BaseModel):
    pattern: alex.definitions.Pattern
    layout: typing.List[int]
    fitness: float
    runtime: float
    runtime_dev: float
