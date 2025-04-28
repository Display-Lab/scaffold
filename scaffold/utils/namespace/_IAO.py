from rdflib import Namespace, URIRef

from scaffold.utils.namespace import AliasingDefinedNamespace


class IAO(AliasingDefinedNamespace):
    _NS = Namespace("http://purl.obolibrary.org/obo/")

    # http://www.w3.org/1999/02/22-rdf-syntax-ns#Property

    IAO_0000136: URIRef
    is_about: URIRef

    _alias = {
        "is_about": "IAO_0000136",
    }
