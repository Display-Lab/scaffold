from urllib.parse import urljoin
from urllib.request import urlopen

import yaml
from loguru import logger
from rdflib import Graph

from scaffold.utils.utils import set_logger

set_logger()


def manifest_to_graph(manifest_path: str) -> Graph:
    g: Graph = Graph()

    try:
        with urlopen(manifest_path) as f:
            manifest_file = yaml.safe_load(f.read().decode("utf-8"))
    except Exception as e:
        logger.error(f"Error loading manifest: {e}")
        return g  # Return an empty graph if the manifest cannot be loaded

    for key, values in manifest_file.items():
        base = urljoin(manifest_path, key)
        for value in values:
            file = urljoin(base, value)
            try:
                with urlopen(file) as f:
                    file_content = f.read().decode("utf-8")

                temp_graph = Graph().parse(data=file_content, format="json-ld")
                g += temp_graph

                logger.debug(f"Graphed file {file}")
            except Exception as e:
                logger.error(f"Error processing item {file}: {e}")
                continue

    return g
