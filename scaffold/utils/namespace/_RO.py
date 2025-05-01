from rdflib import Namespace, URIRef

from scaffold.utils.namespace import AliasingDefinedNamespace


class RO(AliasingDefinedNamespace):
    _NS = Namespace("http://purl.obolibrary.org/obo/")

    # http://www.w3.org/1999/02/22-rdf-syntax-ns#Property

    RO_0000091: URIRef
    has_disposition: URIRef

    _alias = {
        "has_disposition": "RO_0000091",
    }
