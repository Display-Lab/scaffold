# External scaffold.esteemer plugin guide

You can provide your own candidate selection logic as a standalone Python package.

SCAFFOLD discovers Esteemer plugins through Python entry points in the scaffold.esteemer group.

## 1. Create a plugin package

Example structure:

```text
my-scaffold-esteemer/
  pyproject.toml
  src/
    my_scaffold_esteemer/
      __init__.py
      plugin.py
```
## 2. Add scaffold-sdk to your package
If you are using uv the following command will add scaffold-sdk as a dependency to your package:
```
uv add https://github.com/Display-Lab/scaffold/releases/download/v2.1.4/scaffold_sdk-0.1.0-py3-none-any.whl
```

So your pyproject.toml will include the following:
```toml
...
dependencies = [
  "scaffold-sdk",
]

[tool.uv.sources]
scaffold-sdk = { url = "https://github.com/Display-Lab/scaffold/releases/download/v2.1.4/scaffold_sdk-0.1.0-py3-none-any.whl" }
```

## 3. Add plugin metadata and entry point

In your plugin pyproject.toml:

```toml
[project]
name = "my-scaffold-esteemer"
version = "0.1.0"
requires-python = ">=3.12,<3.14"
dependencies = [
  "scaffold-sdk",
]

[project.entry-points."scaffold.esteemer"]
my_plugin = "my_scaffold_esteemer.plugin:MyPluginEsteemer"

[tool.setuptools.packages.find]
where = ["src"]

[tool.uv.sources]
scaffold-sdk = { url = "https://github.com/Display-Lab/scaffold/releases/download/v2.1.4/scaffold_sdk-0.1.0-py3-none-any.whl" }
```

## 3. Implement the Esteemer class

In src/my_scaffold_esteemer/plugin.py:

```python
from rdflib import RDF, URIRef

from scaffold_sdk import Esteemer


class MyPluginEsteemer(Esteemer):
    def select_candidate(self):
        # Basic example: choose the first acceptable candidate.
        candidate_type = URIRef("http://example.com/slowmo#Candidate")
        acceptable_by = URIRef("http://example.com/slowmo#AcceptableBy")

        for subject in self.subject_graph.subjects(RDF.type, candidate_type):
            if self.subject_graph.value(subject, acceptable_by) is not None:
                return self.subject_graph.resource(subject)

        return None

    def version(self) -> str:
        return "0.1.0"
```

Notes:
- Your class must inherit from scaffold_sdk.Esteemer.
- The constructor is provided by the base class and receives context.
- The version() return value must match the configured plugin version.

## 4. Install the plugin in the same environment as SCAFFOLD

```zsh
python -m pip install -e /path/to/my-scaffold-esteemer
```

## 5. Activate the plugin in your knowledge-base config

In your knowledge-base config.yaml:

```yaml
plugins:
  scaffold.esteemer:
    name: my_plugin
    version: "0.1.0"
```

name must match the entry-point key (my_plugin above), and version must match version() from your plugin class.

## 6. Point SCAFFOLD to the config file
The SCAFFOLD environment file (.env) should point to the config file:
```
config=file:///path/to/the/config/file/config.yaml
```

## 7. Run SCAFFOLD

Run pipeline batch or pipeline batch-csv as usual. SCAFFOLD will load the configured plugin and raise a clear error if:
- the plugin is not installed,
- the entry-point name does not match,
- or the plugin version does not match.
