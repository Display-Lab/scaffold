"""Utilty classes for namespace management

`AliasingDefinedNamespace` base class, and `PSDO`, `CPO`, and `SLOWMO` namespaces. These namespaces work the same way as the builtin RDF classes but allow for convenient aliases (e.g. labels) in code.
"""

from rdflib.namespace import (
    _DFNS_RESERVED_ATTRS,
    DefinedNamespace,
    DefinedNamespaceMeta,
)
from rdflib.term import URIRef


class AliasingDefinedNamespaceMeta(DefinedNamespaceMeta):
    _fail = True  # Default is closed namepaces only: fail if neither attribute nor in _extras
    _alias: dict[str, str] = {}

    _DFNS_RESERVED_ATTRS.add("_alias")

    def __getitem__(cls, name: str, default=None) -> URIRef:
        name_or_alias = cls._alias.get(name, name)
        return super().__getitem__(name_or_alias)


class AliasingDefinedNamespace(
    DefinedNamespace, metaclass=AliasingDefinedNamespaceMeta
):
    """Shorthand for defined namespace classes that use aliases. Derived namespace classes should be imported directly and not instantiated.

    The base URI of the namespace is set in the derived class using:
    ```
        _NS = Namespace("http://purl.obolibrary.org/obo/")
    ```

    Terms should be added as class attributes of type `URIRef`:
    ```
        PSDO_00123: URIRef
    ```
    Aliases added as attributes should appear in the `_alias` dictionary and will be automatically mapped.
    ```
        foo: URIRef
        _alias['foo'] = 'PSDO_00123'
        # PSDO.foo == URIRef("http://purl.obolibrary.org/obo/PSDO_00123")
    ```

    Add attributes for aliases directly to the class and map to term attributes using the `_alias` dictionary: `_alias['baz'] = 'PSDO_000125`. Adding an alias  to the `_alias` dictionary without a corresponding class attribute will work fine, but the attribute will not be available for code completion (in the IDE) and it will not appear in the context (if generated)

    All class attributes of type URIRef, including aliases, will appear in the generated context using `as_jsonld_context(pfx='xyz')`.

    The namespace will also be closed by defualt. Set `_fail = False` to allow any URI to be contstructed, or add to the namespace using `_extras.append(term: str)`
    """

    pass


# import at end to avoid circular reference when namespaces import `AliasingDefinedNamespace`
from scaffold.utils.namespace._CPO import CPO  # noqa: E402
from scaffold.utils.namespace._IAO import IAO  # noqa: E402
from scaffold.utils.namespace._PSDO import PSDO  # noqa: E402
from scaffold.utils.namespace._RO import RO  # noqa: E402
from scaffold.utils.namespace._SCHEMA import SCHEMA  # noqa: E402
from scaffold.utils.namespace._SLOWMO import SLOWMO  # noqa: E402

_NAMESPACE_PREFIXES_PFP = {
    "psdo": PSDO,
    "cpo": CPO,
    "slowmo": SLOWMO,
    "ro": RO,
    "iao": IAO,
    "schema": SCHEMA,
}
