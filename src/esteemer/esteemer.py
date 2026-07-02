from abc import ABC, abstractmethod

from rdflib import Graph


class Esteemer(ABC):
    _instances = {}
    _env_loaded = False

    @abstractmethod
    def select_candidate(self):
        pass
    
    @abstractmethod
    def version(self) -> str:
        pass

    def __new__(cls, *args, **kwargs):
        if cls not in cls._instances:
            instance = super().__new__(cls)
            cls._instances[cls] = instance
        return cls._instances[cls]

    def __init__(self, context):
        self.performance_month = context.performance_month
        self.subject = context.subject
        self.req_info =context.request_info
        self.subject_graph=context.subject_graph

        if not getattr(self, "_initialized", False):
            self._initialize()
            self._initialized = True

    def _initialize(self):
        pass
