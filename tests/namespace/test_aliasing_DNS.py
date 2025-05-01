import pytest
from rdflib import Namespace, URIRef

from scaffold.utils.namespace import (
    AliasingDefinedNamespace,
)


def test_basic_defined_namespace_works():
    class NS(AliasingDefinedNamespace):
        _NS = Namespace("http://example.org/")

        FOO: URIRef
        BAR: URIRef

    # Test basic attribute lookup
    assert NS.FOO and NS.BAR in NS
    assert URIRef("http://example.org/FOO") == NS.FOO
    assert NS.FOO != NS.BAR

    # Tesing missing and extra attributes
    with pytest.raises(AttributeError):
        NS.BAZ
    NS._extras.append("BAZ")
    assert NS.BAZ in NS
    assert URIRef("http://example.org/BAZ") == NS.BAZ

    # Test context creation
    assert "ns:FOO" == NS.as_jsonld_context("ns")["@context"]["FOO"]

    with pytest.raises(KeyError):
        NS.as_jsonld_context("ns")["@context"]["BAZ"]


def test_alias():
    """Aliases resolve to the original term in code"""

    class NS(AliasingDefinedNamespace):
        _NS = Namespace("http://example.org/")

        FOO: URIRef
        bar: URIRef

        _alias = {"bar": "FOO"}

    # Test basic attribute lookup
    assert NS.FOO and NS.bar in NS
    assert URIRef("http://example.org/FOO") == NS.FOO
    assert URIRef("http://example.org/FOO") == NS.bar
    assert NS.FOO == NS.bar
    assert NS.bar == NS.FOO


def test_context_with_alias():
    """Currently aliases do not resolve to the original term in the json-ld context"""

    class NS(AliasingDefinedNamespace):
        _NS = Namespace("http://example.org/")

        FOO: URIRef
        bar: URIRef

        _alias = {"bar": "FOO"}

    assert NS.bar == NS.FOO
    terms = NS.as_jsonld_context("ns")["@context"]
    assert terms["ns"] == "http://example.org/"
    assert terms["FOO"] == "ns:FOO"
    assert terms["bar"] != terms["FOO"]


def test_alias_without_attribute():
    class NS(AliasingDefinedNamespace):
        _NS = Namespace("http://example.org/")

        FOO: URIRef

        _alias = {"baz": "FOO"}

    # Test alias without attribute
    # No need to add alias to _extras, non-attribute alias is handled directly
    assert NS.baz in NS
    assert NS.baz == NS.FOO
