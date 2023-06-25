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

    class Config:
        frozen = True


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

    class Config:
        frozen = True


class CacheHierarchy(pydantic.BaseModel):
    caches: dict[str, Cache]
    memory: MainMemory

    class Config:
        frozen = True

    @staticmethod
    def fromYamlFile(f):
        return CacheHierarchy(**yaml.safe_load(f))


class BenchmarkInputElement(pydantic.BaseModel):
    pattern: alex.definitions.Pattern
    layout: typing.Tuple[int, ...]

    class Config:
        frozen = True


class BenchmarkOutput(pydantic.BaseModel):
    pattern: alex.definitions.Pattern
    layout: typing.Tuple[int, ...]
    fitness: float
    runtime: float
    runtime_dev: float

    class Config:
        frozen = True
