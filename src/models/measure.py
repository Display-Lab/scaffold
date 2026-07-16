from dataclasses import dataclass


@dataclass(frozen=True)
class Measure:
    identifier: str
    name: str
    title: str
    measure_type: str
    improvement_notation: str
