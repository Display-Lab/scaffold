import random
from typing import List
from rdflib import RDF, BNode, Graph, URIRef


def measures(performer_graph: Graph) -> List[BNode]:
    """
    returns performer measures.

    Parameters:
    - performer_graph (Graph): The performer_graph.

    Returns:
    List[BNode]: returns list of performer measures.
    """
    measures = performer_graph.objects(
        URIRef("http://example.com/app#display-lab"),
        URIRef("http://example.com/slowmo#IsAboutMeasure"),
    )
    measure_list = list(measures)
    return measure_list


def measure_acceptable_candidates(
    performer_graph: Graph, measure: BNode
) -> List[BNode]:
    """
    extracts the list of acceptable candidates for a measure and applies measure business rules.

    Parameters:
    - performer_graph (Graph): The performer_graph.
    - measure (BNode): The measure.

    Returns:
    List[BNode]: returns list of acceptible candidates.
    """
    # extract the list of acceptible candidates for a measure
    candidate_list = measure_candidates(performer_graph, measure)


    # apply measure business rules
    candidate_list = apply_measure_business_rules(performer_graph, candidate_list)

    return candidate_list


def measure_candidates(performer_graph: Graph, measure: BNode) -> List[BNode]:
    """
    returns acceptible candidate messages for given measure.

    Parameters:
    - performer_graph (Graph): The performer_graph.
    - measure (BNode): The measure.

    Returns:
    List[BNode]: returns list of candidate messages of a measure.
    """
    candidate_messages = [
        subject
        for subject in performer_graph.subjects(
            predicate=URIRef("http://example.com/slowmo#RegardingMeasure"),
            object=measure,
        )
        if(
            (subject, RDF.type, URIRef("http://example.com/slowmo#Candidate"))
            in performer_graph
            and (subject, URIRef("slowmo:acceptable_by"), None)
            in performer_graph
        )
    ]
    return candidate_messages


def apply_measure_business_rules(
    performer_graph: Graph, candidate_list: List[BNode]
) -> List[BNode]:
    """
    applies measure business rules on candidate messages of a measure.

    Parameters:
    - performer_graph (Graph): The performer_graph.
    - candidate_list (List[BNode]): The candidate list.

    Returns:
    List[BNode]: returns the updated candidate list.
    """
    return candidate_list


def render(performer_graph: Graph, candidate: BNode) -> BNode:
    """
    creates selected message from a selected candidate.

    Parameters:
    - performer_graph (Graph): The performer_graph.
    - candidate (BNode): The candidate.

    Returns:
    BNode: selected message.
    """
    s_m = {}
    a = 0
    # print(self.node)
    if candidate is None:
        s_m["message_text"] = "No message selected"
        return s_m
    else:
        s = candidate
        temp_name = URIRef("http://example.com/slowmo#name")  # URI of template name?
        p232 = URIRef("psdo:PerformanceSummaryDisplay")
        Display = ["text only", "bar chart", "line graph"]
        comparator_types = ["Top 25", "Top 10", "Peers", "Goal"]
        sw = 0
        o2wea = []

        ## Format selected_candidate to return for pictoralist-ing
        for s21, p21, o21 in performer_graph.triples(
            (s, URIRef("http://example.com/slowmo#AncestorTemplate"), None)
        ):
            s_m["template_id"] = o21
        # Duplicate logic above and use to pull template name
        for s21, p21, o21 in performer_graph.triples((s, temp_name, None)):
            s_m["template_name"] = o21

        for s2, p2, o2 in performer_graph.triples(
            (s, URIRef("psdo:PerformanceSummaryTextualEntity"), None)
        ):
            s_m["message_text"] = o2
        # for s212,p212,o212 in self.spek_tp.triples((s,p232,None)):

        s_m["display"] = random.choice(Display)
        # for s9,p9,o9 in self.spek_tp.triples((s,p8,None)):
        #     s_m["Comparator Type"] = o9
        for s2we, p2we, o2we in performer_graph.triples(
            (s, URIRef("slowmo:acceptable_by"), None)
        ):
            o2wea.append(o2we)
        # print(*o2wea)
        s_m["acceptable_by"] = o2wea

        comparator_list = []

        for s5, p5, o5 in performer_graph.triples(
            (s, URIRef("http://purl.obolibrary.org/obo/RO_0000091"), None)
        ):
            s6 = o5
            # print(o5)
            for s7, p7, o7 in performer_graph.triples(
                (s6, URIRef("http://example.com/slowmo#RegardingMeasure"), None)
            ):
                s_m["measure_name"] = o7
                s10 = BNode(o7)
                for s11, p11, o11 in performer_graph.triples(
                    (s10, URIRef("http://purl.org/dc/terms/title"), None)
                ):
                    s_m["measure_title"] = o11
            for s14, p14, o14 in performer_graph.triples((s6, RDF.type, None)):
                # print(o14)
                if o14 == URIRef("http://purl.obolibrary.org/obo/PSDO_0000128"):
                    comparator_list.append("Top 25")
                    # s_m["comparator_type"]="Top 25"
                if o14 == URIRef("http://purl.obolibrary.org/obo/PSDO_0000129"):
                    comparator_list.append("Top 10")
                    # s_m["comparator_type"]="Top 10"
                if o14 == URIRef("http://purl.obolibrary.org/obo/PSDO_0000126"):
                    comparator_list.append("Peers")
                    # s_m["comparator_type"]="Peers"
                if o14 == URIRef("http://purl.obolibrary.org/obo/PSDO_0000094"):
                    comparator_list.append("Goal")
                    # s_m["comparator_type"]="Goal"
        for i in comparator_list:
            if i is not None:
                a = i
        s_m["comparator_type"] = a
        return s_m
