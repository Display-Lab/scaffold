import random

from rdflib import RDF, Graph, Literal, URIRef
from rdflib.resource import Resource

from src.esteemer.esteemer import Esteemer


class Random_candidate_selector(Esteemer):
    def _initialize(self):
        pass
        
    def version(self) -> str:
        return "1.0.1"
    
    def select_candidate(self, performer_graph: Graph) -> Resource:
        """
        randomly selects a candidate.

        Parameters:
        - performer_graph (Graph): The performer_graph .

        Returns:
        BNode: selected candidate.
        """
        
        candidates = [
            performer_graph.resource(subject)
            for subject in performer_graph.subjects(
                RDF.type,
                URIRef("http://example.com/slowmo#Candidate")
            )
            if (subject,
                URIRef("http://example.com/slowmo#AcceptableBy"),
                None) in performer_graph
        ]  
    
        selected_candidate = random.choice(candidates)
        
        selected_candidate[URIRef("http://example.com/slowmo#Selected")] = Literal(True)

        return selected_candidate