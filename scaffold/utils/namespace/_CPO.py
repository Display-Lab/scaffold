from rdflib import Namespace, URIRef

from scaffold.utils.namespace import AliasingDefinedNamespace


class CPO(AliasingDefinedNamespace):
    _NS = Namespace("http://purl.obolibrary.org/obo/")

    cpo_0000029: URIRef
    causal_pathway: URIRef

    cpo_0000056: URIRef
    has_causal_pathway: URIRef

    _alias = {
        "causal_pathway": "cpo_0000029",
        "has_causal_pathway": "cpo_0000056",
    }
