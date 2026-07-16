from rdflib import RDF, Graph

from src.utils.namespace import FHIR

from .measure import Measure


class MeasureCatalog:
    @classmethod
    def from_graph(cls, graph: Graph) -> "MeasureCatalog":
        measures = []

        for subject in graph.subjects(RDF.type, FHIR.Measure):
            measures.append(
                Measure(
                    identifier=str(graph.value(subject, FHIR.identifier)),
                    name=str(graph.value(subject, FHIR.name)),
                    title=str(graph.value(subject, FHIR.title)),
                    measure_type=str(graph.value(subject, FHIR.type)),
                    improvement_notation=str(graph.value(subject, FHIR.improvementNotation)),
                )
            )

        return cls(measures)
    
    def __init__(self, measures: list[Measure]):
        self._measures = measures
        self._by_name = {m.name: m for m in measures}
        self._by_identifier = {m.identifier: m for m in measures}

    def __iter__(self):
        return iter(self._measures)

    def __getitem__(self, name: str) -> Measure:
        return self._by_name[name]
    
    def __contains__(self, identifier: str) -> bool:
        return identifier in self._by_identifier    

    def get(self, name: str) -> Measure | None:
        return self._by_name.get(name)

    def improvement_notation(self, name: str) -> str | None:
        measure = self.get(name)
        return None if measure is None else measure.improvement_notation