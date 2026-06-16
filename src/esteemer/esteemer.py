from abc import ABC, abstractmethod

from rdflib import Graph


class Esteemer(ABC):
    _instances = {}
    _env_loaded = False

    @abstractmethod
    def select_candidate(self, performer_graph: Graph):
        pass

    def __new__(cls, *args, **kwargs):
        if cls not in cls._instances:
            instance = super().__new__(cls)
            cls._instances[cls] = instance
        return cls._instances[cls]

    def __init__(self, performance_month: str, subject: str):
        self.performance_month = performance_month
        self.subject = subject

        if not getattr(self, "_initialized", False):
            self._initialize()
            self._initialized = True

    def _initialize(self):
        pass
