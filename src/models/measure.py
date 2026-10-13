from dataclasses import dataclass

from rdflib import RDF, Graph

from src.utils.namespace import FHIR


@dataclass(frozen=True)
class Measure:
    identifier: str
    name: str
    title: str
    measure_type: str
    improvement_notation: str

    def to_json(self) -> dict[str, object]:
        return {
            "resourceType": "Measure",
            "id": self.identifier,
            "identifier": [{"value": self.identifier}],
            "name": self.name,
            "title": self.title,
            "status": "active",
            "type": [{"text": self.measure_type}],
            "improvementNotation": {"text": self.improvement_notation},
        }

    @classmethod
    def from_graph(cls, graph: Graph) -> dict[str, "Measure"]:
        measures: dict[str, Measure] = {}

        for subject in graph.subjects(RDF.type, FHIR.Measure):
            identifier = str(graph.value(subject, FHIR.identifier))
            measures[identifier] = cls(
                identifier=identifier,
                name=str(graph.value(subject, FHIR.name)),
                title=str(graph.value(subject, FHIR.title)),
                measure_type=str(graph.value(subject, FHIR.type)),
                improvement_notation=str(graph.value(subject, FHIR.improvementNotation)),
            )

        return measures
