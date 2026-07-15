from rdflib import Namespace, URIRef

from src.utils.namespace import AliasingDefinedNamespace


class FHIR(AliasingDefinedNamespace):
    _NS = Namespace("http://hl7.org/fhir/")

    Measure: URIRef
    measure_identifier: URIRef
    measure_name: URIRef
    measure_title: URIRef
    measure_group: URIRef
    measure_group_type: URIRef
    measure_group_improvement_notation: URIRef

    # Legacy aliases retained for compatibility with existing data/code.
    identifier: URIRef
    name: URIRef
    title: URIRef
    group: URIRef
    type: URIRef
    improvementNotation: URIRef

    # Terms that are not valid Python attribute names but are needed for URI mapping.
    _extras = [
        "Measure.identifier",
        "Measure.name",
        "Measure.title",
        "Measure.group",
        "Measure.group.type",
        "Measure.group.improvementNotation",
    ]

    _alias = {
        "measure_identifier": "Measure.identifier",
        "measure_name": "Measure.name",
        "measure_title": "Measure.title",
        "measure_group": "Measure.group",
        "measure_group_type": "Measure.group.type",
        "measure_group_improvement_notation": "Measure.group.improvementNotation",
        "identifier": "Measure.identifier",
        "name": "Measure.name",
        "title": "Measure.title",
        "group": "Measure.group",
        "type": "Measure.group.type",
        "improvementNotation": "Measure.group.improvementNotation",
    }