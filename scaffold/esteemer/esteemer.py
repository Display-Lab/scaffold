import random
from datetime import datetime
from typing import List

from rdflib import XSD, BNode, Graph, Literal, URIRef
from rdflib.resource import Resource

from scaffold.bitstomach.signals import (
    Achievement,
    Approach,
    Comparison,
    Loss,
    Signal,
    Trend,
)
from scaffold.context import get_history, get_preferences
from scaffold.esteemer import utils
from scaffold.esteemer.signals import History
from scaffold.utils.namespace import PSDO, SLOWMO
from scaffold.utils.settings import settings


def score(candidate: Resource, MPM: dict, performance_month) -> Resource:
    """
    calculates score.

    Parameters:
    - candidate_resource (Resource): The candidate resource.
    - history (json): The message history.
    - preferences (json): The performer preferences.

    Returns:
    float: score.
    """

    staff_number = candidate.graph.value(
        BNode("p1"), URIRef("http://example.com/slowmo#IsAboutPerformer")
    ).value

    history = get_history(staff_number)
    preferences = get_preferences(staff_number)["Message_Format"]

    CAUSAL_PATHWAY = {
        "Social Better": {"score": score_better, "rules": rule_social_highest},
        "Social Worse": {"score": score_worse, "rules": null_rule},
        "Improving": {"score": score_improving, "rules": null_rule},
        "Worsening": {"score": score_worsening, "rules": null_rule},
        "Goal Gain": {"score": score_gain, "rules": null_rule},
        "Goal Loss": {"score": score_loss, "rules": null_rule},
        "Social Gain": {"score": score_gain, "rules": rule_social_highest},
        "Social Loss": {"score": score_loss, "rules": rule_social_lowest},
        "Goal Worse": {"score": score_worse, "rules": null_rule},
        "Goal Approach": {"score": score_approach, "rules": null_rule},
        "Social Approach": {"score": score_approach, "rules": rule_social_lowest},
    }

    causal_pathway = candidate.value(SLOWMO.AcceptableBy).value
    motivating_informations = list(candidate[PSDO.motivating_information])
    rules = CAUSAL_PATHWAY[causal_pathway]["rules"]
    score_mi = CAUSAL_PATHWAY[causal_pathway]["score"]

    # rules

    if not rules(candidate):
        return None

    # MI
    if settings.use_mi:
        mi_score = score_mi(candidate, motivating_informations, MPM[causal_pathway])
    else:
        mi_score = 0.0

    candidate[URIRef("motivating_score")] = Literal(mi_score, datatype=XSD.double)

    # History
    history_score = score_history(
        candidate, history, MPM[causal_pathway], performance_month
    )
    candidate[URIRef("history_score")] = Literal(history_score, datatype=XSD.double)

    # Preferences
    preference_score = score_preferences(candidate, preferences)
    candidate[URIRef("preference_score")] = Literal(
        preference_score, datatype=XSD.double
    )

    # coachiness
    coachiness_score = MPM[causal_pathway]["coachiness"]
    candidate[URIRef("coachiness_score")] = Literal(
        coachiness_score, datatype=XSD.double
    )

    final_calculated_score = final_score(mi_score, history_score, preference_score)

    candidate[SLOWMO.Score] = Literal(final_calculated_score, datatype=XSD.double)

    return candidate


def final_score(m, h, p):
    """
    the function, final_score,  takes two inputs, s and p. the range for s is 0 to 1. the range for p is -2 to +2.  The function f(s,p) increases with either s or p increasing. The function should have the following constraints: f(1,-2) == f(.5, 0) == f(0,2) and f(0.5, -2) == f(0.25, -1) == f(0, 0).
    """

    score = m * 1 + h * 2 + p * 1.3

    return round(score, 2)


def score_better(
    candidate: Resource, motivating_informations: List[Resource], mpm: dict
) -> float:
    moderators = comparator_moderators(candidate, motivating_informations, Comparison)

    score = moderators["comparison_size"]  # * mpm["comparison_size"]

    return score


def null_rule(candidate):
    return True


def rule_social_highest(candidate: Resource):
    # TODO: see if we can refactor to a better query
    causal_pathway = candidate.value(SLOWMO.AcceptableBy).value
    if candidate[SLOWMO.RegardingComparator : PSDO.peer_average_comparator]:
        candidates = utils.candidates(
            candidate.graph,
            candidate.value(SLOWMO.RegardingMeasure).identifier,
            filter_acceptable=True,
        )
        return not any(
            (
                candid[SLOWMO.RegardingComparator : PSDO.peer_90th_percentile_benchmark]
                or candid[
                    SLOWMO.RegardingComparator : PSDO.peer_75th_percentile_benchmark
                ]
            )
            and candid.value(SLOWMO.AcceptableBy).value == causal_pathway
            for candid in candidates
        )

    if candidate[SLOWMO.RegardingComparator : PSDO.peer_75th_percentile_benchmark]:
        candidates = utils.candidates(
            candidate.graph,
            candidate.value(SLOWMO.RegardingMeasure).identifier,
            filter_acceptable=True,
        )
        return not any(
            candid[SLOWMO.RegardingComparator : PSDO.peer_90th_percentile_benchmark]
            and candid.value(SLOWMO.AcceptableBy).value == causal_pathway
            for candid in candidates
        )

    return True


def rule_social_lowest(candidate: Resource):
    # TODO: see if we can refactor to a better query
    causal_pathway = candidate.value(SLOWMO.AcceptableBy).value
    if candidate[SLOWMO.RegardingComparator : PSDO.peer_90th_percentile_benchmark]:
        candidates = utils.candidates(
            candidate.graph,
            candidate.value(SLOWMO.RegardingMeasure).identifier,
            filter_acceptable=True,
        )
        return not any(
            (
                candid[SLOWMO.RegardingComparator : PSDO.peer_average_comparator]
                or candid[
                    SLOWMO.RegardingComparator : PSDO.peer_75th_percentile_benchmark
                ]
            )
            and candid.value(SLOWMO.AcceptableBy).value == causal_pathway
            for candid in candidates
        )

    if candidate[SLOWMO.RegardingComparator : PSDO.peer_75th_percentile_benchmark]:
        candidates = utils.candidates(
            candidate.graph,
            candidate.value(SLOWMO.RegardingMeasure).identifier,
            filter_acceptable=True,
        )
        return not any(
            candid[SLOWMO.RegardingComparator : PSDO.peer_average_comparator]
            and candid.value(SLOWMO.AcceptableBy).value == causal_pathway
            for candid in candidates
        )

    return True


def score_worse(
    candidate: Resource, motivating_informations: List[Resource], mpm: dict
) -> float:
    moderators = comparator_moderators(candidate, motivating_informations, Comparison)

    score = moderators["comparison_size"]  # * mpm["comparison_size"]

    return score


def score_improving(
    candidate: Resource, motivating_informations: List[Resource], mpm: dict
) -> float:
    moderators = Trend.moderators(motivating_informations)[0]

    score = moderators["trend_size"]  # * mpm["trend_size"]

    return score


def score_worsening(
    candidate: Resource, motivating_informations: List[Resource], mpm: dict
) -> float:
    # TODO: what should the response be if the candidate is not acceptable by worsening
    moderators = Trend.moderators(motivating_informations)[0]

    score = moderators["trend_size"]  # * mpm["trend_size"]

    return score


def score_approach(
    candidate: Resource, motivating_informations: List[Resource], mpm: dict
) -> float:
    moderators = comparator_moderators(candidate, motivating_informations, Approach)

    score = (
        moderators["comparison_size"] * mpm["comparison_size"]
        + moderators["trend_size"] * mpm["trend_size"]
        + moderators["achievement_recency"] * mpm["achievement_recency"]
    ) / (mpm["comparison_size"] + mpm["trend_size"] + mpm["achievement_recency"])

    return score


def score_gain(
    candidate: Resource, motivating_informations: List[Resource], mpm: dict
) -> float:
    moderators = comparator_moderators(candidate, motivating_informations, Achievement)

    score = (
        moderators["comparison_size"] * mpm["comparison_size"]
        + moderators["trend_size"] * mpm["trend_size"]
        + moderators["achievement_recency"] * mpm["achievement_recency"]
    ) / (mpm["comparison_size"] + mpm["trend_size"] + mpm["achievement_recency"])

    return score


def score_loss(
    candidate: Resource, motivating_informations: List[Resource], mpm: dict
) -> float:
    moderators = comparator_moderators(candidate, motivating_informations, Loss)

    score = (
        moderators["comparison_size"] * mpm["comparison_size"]
        + moderators["trend_size"] * mpm["trend_size"]
        + moderators["loss_recency"] * mpm["loss_recency"]
    ) / (mpm["comparison_size"] + mpm["trend_size"] + mpm["loss_recency"])

    return score


def comparator_moderators(candidate, motivating_informations, signal: Signal):
    comparator_type = candidate.value(SLOWMO.RegardingComparator).identifier

    moderators = signal.moderators(motivating_informations)

    scoring_detail = [
        moderator
        for moderator in moderators
        if moderator["comparator_type"] == comparator_type
    ][0]

    return scoring_detail


def score_history(candidate: Resource, history, mpm: dict, performance_month) -> float:
    """
    calculates history sub-score.

    Parameters:
    - candidate_resource (Resource): The candidate resource.
    - history (dict): The history of messages.

    Returns:
    float: history sub-score.
    """
    if not history or not settings.use_history:
        return 1.0

    # turn candidate resource into a 'history' element for the current month
    g: Graph = candidate.graph

    signals = History.detect(
        history,
        {datetime.fromisoformat(performance_month): History.to_element(candidate)},
    )

    if not signals:
        return 1.0

    mod = History.moderators(signals)[0]

    history_moderator = (
        mod["message_recurrence"] * mpm["message_recurrence"]
        + mod["message_recency"] * mpm["message_recency"]
        + mod["measure_recency"] * mpm["measure_recency"]
    ) / (mpm["message_recurrence"] + mpm["message_recency"] + mpm["measure_recency"])

    return 1 - history_moderator * mpm["history"]


def score_preferences(candidate_resource: Resource, preferences: dict) -> float:
    """
    calculates preference sub-score.

    Parameters:
    - candidate_resource (Resource): The candidate resource.
    - preferences (json): The performer preferences.

    Returns:
    float: preference sub-score.
    """

    if not settings.use_preferences:
        return 0.0

    return preferences.get(str(candidate_resource.value(SLOWMO.AcceptableBy).value).lower(), 0.0)


def select_candidate(performer_graph: Graph) -> BNode:
    """
    applies between measure business rules and selects the candidate based on scores.

    Parameters:
    - performer_graph (Graph): The performer_graph .

    Returns:
    BNode: selected candidate.
    """
    # 1. apply between measure business rules (future)

    # 2. select candidate

    # Find the max score
    if not set(performer_graph[: SLOWMO.AcceptableBy :]):
        return None

    # filter acceptable candidates
    candidates = utils.candidates(performer_graph, filter_acceptable=True)

    # filter scored candidates
    candidates = [
        candidate
        for candidate in candidates
        if (candidate.value(URIRef("coachiness_score")) is not None)
    ]

    if settings.use_coachiness:
        # filter highest coachiness candidates
        highest_coachiness_candidates = candidates_from_coachiness_category(
            candidates, category=1.0
        )
        if not highest_coachiness_candidates:
            highest_coachiness_candidates = candidates_from_coachiness_category(
                candidates, category=0.5
            )
        if highest_coachiness_candidates:
            candidates = highest_coachiness_candidates

    max_score = max(
        [candidate.value(SLOWMO.Score).value for candidate in candidates],
        default=None,
    )

    candidates_with_max_score = [
        (candidate.identifier)
        for candidate in candidates
        if candidate.value(SLOWMO.Score).value == max_score
    ]

    # Randomly select one of the candidates with the known maximum score
    selected_candidate = random.choice(candidates_with_max_score)

    performer_graph.add((selected_candidate, SLOWMO.Selected, Literal(True)))

    return selected_candidate


def candidates_from_coachiness_category(candidates, category):
    return [
        candidate
        for candidate in candidates
        if (candidate.value(URIRef("coachiness_score")).value == category)
    ]
