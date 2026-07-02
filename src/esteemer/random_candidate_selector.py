import random

from rdflib import RDF, Graph, Literal, URIRef
from rdflib.resource import Resource
from scaffold_sdk.esteemer import Esteemer


class Random_candidate_selector(Esteemer):
    def _initialize(self):
        pass
        
    def version(self) -> str:
        return "1.0.1"
    
    def select_candidate(self) -> Resource:
        """
        randomly selects a candidate.        

        Returns:
        BNode: selected candidate.
        """
        subject_graph = self.subject_graph
        candidates = [
            subject_graph.resource(subject)
            for subject in subject_graph.subjects(
                RDF.type,
                URIRef("http://example.com/slowmo#Candidate")
            )
            if (subject,
                URIRef("http://example.com/slowmo#AcceptableBy"),
                None) in subject_graph
        ]  
    
        selected_candidate = random.choice(candidates)
        
        selected_candidate[URIRef("http://example.com/slowmo#Selected")] = Literal(True)

        return selected_candidate