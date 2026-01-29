from typing import List

from rdflib import RDF, BNode, Graph, URIRef
from rdflib.resource import Resource

from scaffold.utils import PSDO
from scaffold import startup

class Signal:
    signal_type: URIRef
    measure_types: List[URIRef]
    
    @classmethod
    def detect(self, performance_df, comparator_df=None):
        raise NotImplementedError("Subclasses must implement detect()")
    
    @classmethod
    def check(self, performance_df):
        """
        checks if the signal can process the measure based on measure type
        """
        node = BNode(performance_df["measure"].iloc[0])
        measure_type = next(startup.base_graph.objects(node, PSDO.has_desired_direction)).value
        if URIRef(measure_type) not in self.measure_types:
            return False
        return True

    @classmethod
    def select(cls, signals: List[Resource]) -> List[Resource]:
        """
        select method filters motivating information using the signal type
        """
        if not signals:
            return []

        return list(
            filter(
                cls.is_rdf_type_of,
                signals,
            )
        )

    @staticmethod
    def moderators(mi: Resource) -> dict:
        """
        creates a dictionary of moderators. base calss adds types
        """
        base_mods = {"type": []}
        for signal_type in mi[RDF.type]:
            base_mods["type"].append(signal_type.identifier)

        return base_mods

    @classmethod
    def _resource(cls) -> Resource:
        """
        creates the base subgraph and adds general types
        """
        # TODO: Refactor to allow optional list of tuples (p, o) to ba added to base node
        base = Graph().resource(BNode())
        base.add(RDF.type, PSDO.motivating_information)
        base.add(RDF.type, cls.signal_type)

        return base

    @classmethod
    def is_rdf_type_of(cls, mi: Resource) -> bool:
        """
        checks whether motivating information is of the same type of the signal
        """
        return cls.signal_type in {t.identifier for t in mi[RDF.type]}

    @classmethod
    def disposition(cls, mi: Resource) -> List[Resource]:
        return list(mi[RDF.type])

    @classmethod
    def for_type(cls, mi: Resource):
        for signal in SIGNALS:
            if signal.is_rdf_type_of(mi):
                return signal

    @classmethod
    def exclude(cls, mi, types: List[Resource]) -> bool:
        return False


# TODO: revisit. at this time must be loaded after Signal and in order Comparison, Trend and then Achievement
from scaffold.bitstomach.signals._comparison import Comparison  # noqa: E402, I001
from scaffold.bitstomach.signals._trend import Trend  # noqa: E402, I001
from scaffold.bitstomach.signals._trend_r import Trend_R  # noqa: E402, I001
from scaffold.bitstomach.signals._achievement import Achievement  # noqa: E402, I001
from scaffold.bitstomach.signals._loss import Loss  # noqa: E402, I001
from scaffold.bitstomach.signals._approach import Approach  # noqa: E402, I001

__all__ = ["Comparison", "Trend", "Trend_R", "Achievement", "Loss", "Approach"]

SIGNALS = {
    Comparison: Signal,
    Trend: Signal,
    Trend_R: Signal,
    Achievement: Signal,
    Loss: Signal,
    Approach: Signal,
}
