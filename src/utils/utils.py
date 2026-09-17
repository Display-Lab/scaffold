import base64
import datetime
import re
import sys
from importlib.metadata import entry_points
from typing import List
from urllib.request import urlopen

import pandas as pd
import yaml
from loguru import logger
from rdflib import RDF, BNode, Graph, URIRef
from rdflib.resource import Resource
from scaffold_sdk import Esteemer

from src import context, startup
from src.models import CommunicationRequest
from src.utils import SLOWMO
from src.utils.namespace import FHIR, PSDO
from src.utils.settings import settings

candidate_df: pd.DataFrame = pd.DataFrame()
response_df: pd.DataFrame = pd.DataFrame()


def analyse_responses():
    global response_df

    r2 = (
        response_df.groupby("causal_pathway")["subject"]
        .agg(count=("count"))
        .reset_index()
    )

    r2["%  "] = round(r2["count"] / r2["count"].sum() * 100, 1)

    print(f"\n {r2} \n")


def analyse_candidates(OUTPUT):
    global candidate_df

    if OUTPUT:
        candidate_df.to_csv(OUTPUT, index=False)

    candidate_df.rename(columns={"acceptable_by": "causal_pathway"}, inplace=True)
    candidate_df["score"] = candidate_df["score"].astype(float)
    candidate_df.rename(columns={"name": "message"}, inplace=True)

    # causal pathways
    causal_pathway_report = build_table("causal_pathway")
    print(causal_pathway_report.to_string(), "\n")

    # messages
    message_report = build_table("message")
    print(message_report.to_string(), "\n")

    # measures
    measure_report = build_table("measure")
    print(measure_report.to_string(), "\n")


def build_table(grouping_column):
    candidate_df["selected1"] = (
        pd.to_numeric(candidate_df["selected"], errors="coerce").fillna(0).astype(int)
    )

    report_table = (
        candidate_df.groupby(grouping_column)["selected1"]
        .agg(acceptable=("count"), selected=("sum"))
        .reset_index()
    )
    scores = round(
        candidate_df.groupby(grouping_column)["score"]
        .agg(acceptable_score=("mean"))
        .reset_index(),
        2,
    )
    report_table = pd.merge(report_table, scores, on=grouping_column, how="left")

    report_table["% acceptable"] = round(
        report_table["acceptable"] / report_table["acceptable"].sum() * 100, 1
    )
    report_table["% selected"] = round(
        report_table["selected"] / report_table["selected"].sum() * 100, 1
    )
    report_table["% of acceptable selected"] = round(
        report_table["selected"] / report_table["acceptable"] * 100, 1
    )
    selected_scores = round(
        candidate_df[candidate_df["selected"]]
        .groupby(grouping_column)["score"]
        .agg(selected_score=("mean"))
        .reset_index(),
        2,
    )
    report_table = pd.merge(
        report_table, selected_scores, on=grouping_column, how="left"
    )

    report_table = report_table[
        [
            grouping_column,
            "acceptable",
            "% acceptable",
            "acceptable_score",
            "selected",
            "% selected",
            "selected_score",
            "% of acceptable selected",
        ]
    ]

    return report_table


def add_candidates(response_data: dict):
    global candidate_df
    data = response_data.get("candidates", None)
    if data:
        candidates = pd.DataFrame(data[1:], columns=data[0])
        candidates["performance_month"] = context.performance_month
        candidate_df = pd.concat([candidate_df, candidates], ignore_index=True)


def _communication_request_response_info(resource: dict) -> tuple:
    """Extract subject and causal pathway from a CommunicationRequest response."""
    subject = None
    causal_pathway = [None]

    reference = resource.get("subject", {}).get("reference")
    if reference:
        subject = reference.split("/", 1)[-1]

    for extension in resource.get("extension", []):
        nested_extensions = extension.get("extension", [])
        for nested in nested_extensions:
            if nested.get("url") != "acceptable_by":
                continue
            value = nested.get("valueString")
            if value:
                causal_pathway = [value]
                return subject, causal_pathway

    return subject, causal_pathway


def add_response(response_data):
    global response_df

    if response_data.get("resourceType") == "CommunicationRequest":
        subject, causal_pathway = _communication_request_response_info(response_data)
    else:
        selected_candidate = response_data.get("selected_candidate", None)
        subject = response_data.get("subject", None)
        causal_pathway = (
            selected_candidate["acceptable_by"] if selected_candidate else [None]
        )

    response_dict: dict = {
        "subject": [subject],
        "causal_pathway": causal_pathway,
    }
    response_df = pd.concat(
        [response_df, pd.DataFrame(response_dict)], ignore_index=True
    )


def extract_number(filename):
    # Extract numeric part from filename
    match = re.search(r"_(\d+)", str(filename))
    if match:
        return int(match.group(1))
    else:
        return float("inf")  # Return infinity if no numeric part found


def set_logger():
    logger.remove()
    logger.add(
        sys.stdout,
        colorize=True,
        format="{level}|  {message}",
        level=settings.log_level,
    )
    logger.at_least = lambda lvl: (
        logger.level(lvl).no >= logger.level(settings.log_level).no
    )


def merge_and_pivot(performance_df):
    # prepare performance data
    performance_enriched = performance_df.merge(
        context.practitioner_role,
        how="left",
        left_on="subject",
        right_on="PractitionerRole.identifier",
    )

    pivoted_comparator = context.comparator_df.pivot_table(
        index=["period.start", "measure", "group.subject", "PractitionerRole.code"],
        columns="group.code",
        values="measureScore.rate",
    ).reset_index()

    final_df = performance_enriched.merge(
        pivoted_comparator,
        how="left",
        left_on=["period.start", "measure"],
        right_on=["period.start", "measure"],
    )

    performance_df = final_df.copy()

    return performance_df


def candidates(
    subject_graph: Graph, measure: BNode = None, filter_acceptable: bool = False
) -> List[Resource]:
    """
    Retrieve a list of candidate resources from the performer graph.

    Parameters:
        subject_graph (Graph): The subject_graph.
        measure (BNode, optional): The measure to filter candidates. Defaults to None.
        filter_acceptable (bool, optional): Whether to filter candidates based on acceptability. Defaults to False.

    Returns:
        List[Resource]: A list of candidate BNodes.
    """

    candidates = [
        subject_graph.resource(subject)
        for subject in subject_graph.subjects(RDF.type, SLOWMO.Candidate)
    ]

    candidates = [
        candidate
        for candidate in candidates
        if (
            (
                measure is None
                or candidate.value(SLOWMO.RegardingMeasure).identifier == measure
            )
            and (
                not filter_acceptable
                or candidate.value(SLOWMO.AcceptableBy) is not None
            )
        )
    ]

    return candidates


def render(subject_graph: Graph, candidate: BNode) -> dict:
    """
    creates selected message from a selected candidate.

    Parameters:
    - subject_graph (Graph): The subject_graph.
    - candidate (BNode): The candidate.

    Returns:
    BNode: selected message.
    """
    s_m = {}

    # print(self.node)
    if candidate is None:
        s_m["message_text"] = "No message selected"
        return s_m
    else:
        temp_name = SLOWMO.name  # URI of template name?
        o2wea = []
        candidate_resource = subject_graph.resource(candidate)

        ## Format selected_candidate to return for pictoralist-ing
        for s21, p21, o21 in subject_graph.triples(
            (candidate, SLOWMO.AncestorTemplate, None)
        ):
            s_m["template_id"] = o21
        # Duplicate logic above and use to pull template name
        for s21, p21, o21 in subject_graph.triples((candidate, temp_name, None)):
            s_m["template_name"] = o21

        for s2, p2, o2 in subject_graph.triples(
            (candidate, URIRef("psdo:PerformanceSummaryTextualEntity"), None)
        ):
            s_m["message_text"] = o2
        # for s212,p212,o212 in self.spek_tp.triples((s,p232,None)):

        s_m["display"] = candidate_resource.value(
            SLOWMO.Display
        ).value  # random.choice(Display)

        # for s9,p9,o9 in self.spek_tp.triples((s,p8,None)):
        #     s_m["Comparator Type"] = o9
        for s2we, p2we, o2we in subject_graph.triples(
            (candidate, SLOWMO.AcceptableBy, None)
        ):
            o2wea.append(o2we)
        # print(*o2wea)
        s_m["acceptable_by"] = o2wea

        measure = candidate_resource.value(SLOWMO.RegardingMeasure)
        s_m["measure_name"] = str(measure.identifier)
        s_m["measure_title"] = measure.value(FHIR.title).value
        s_m["comparator_type"] = candidate_resource.value(
            SLOWMO.RegardingComparator / SLOWMO.DisplayName
        )
        return s_m


def candidates_records(subject_graph: Graph) -> List[List]:
    """
    provides the representation of candidates as a dictionary.

    Parameters:
    - subject_graph (Graph): The subject_graph.

    Returns:
    dict: The representation of candidates as a dictionary.
    """
    candidate_list = [
        [
            "subject",
            "measure",
            "score",
            "motivating_score",
            "history_score",
            "preference_score",
            "coachiness_score",
            "name",
            "acceptable_by",
            "selected",
            "PerformanceGapSize",
            "PerformanceTrendSlope",
            "StreakLength",
            "denominator",
        ]
    ]

    for a_candidate in candidates(subject_graph, filter_acceptable=True):
        # representation = candidate_as_dictionary(a_candidate)
        representation = candidate_as_record(a_candidate)

        candidate_list.append(representation)
    return candidate_list


def candidate_as_record(a_candidate: Resource) -> List:
    representation = []

    representation.append(context.subject)
    representation.append(a_candidate.value(SLOWMO.RegardingMeasure).identifier)
    score = a_candidate.value(SLOWMO.Score)
    representation.append(score)
    representation.append(a_candidate.value(URIRef("motivating_score")))
    representation.append(a_candidate.value(URIRef("history_score")))

    representation.append(a_candidate.value(URIRef("preference_score")))
    representation.append(a_candidate.value(URIRef("coachiness_score")))

    representation.append(a_candidate.value(SLOWMO.name))
    representation.append(a_candidate.value(SLOWMO.AcceptableBy))
    representation.append(bool(a_candidate.value(SLOWMO.Selected)))

    signals = extract_motivating_signals(a_candidate)
    representation.append(
        ""
        if signals["PerformanceGapSize"] is None
        else str(signals["PerformanceGapSize"])
    )
    representation.append(
        ""
        if signals["PerformanceTrendSlope"] is None
        else str(signals["PerformanceTrendSlope"])
    )
    representation.append(
        "" if signals["StreakLength"] is None else str(signals["StreakLength"])
    )

    filtered = context.performance_df[
        (
            context.performance_df["measure"]
            == str(a_candidate.value(SLOWMO.RegardingMeasure).identifier)
        )
        & (context.performance_df["period.start"] == context.performance_month)
    ]

    if len(filtered) != 1:
        raise ValueError(f"Expected exactly 1 row, found {len(filtered)}")

    denominator = filtered.iloc[0]["measureScore.denominator"]
    representation.append(int(denominator))

    return representation


def extract_motivating_signals(a_candidate: Resource) -> list[dict[str, object]]:
    """
    Extracts motivating signal values (performance gap size, trend slope and
    streak length) from a candidate's motivating information.

    Parameters:
    - a_candidate (Resource): The candidate to extract signals from.

    Returns:
    dict: Signal values, keyed by signal name, or None where a signal is not present.
    """
    signals = {
        "PerformanceGapSize": None,
        "PerformanceTrendSlope": None,
        "StreakLength": None,
    }

    for signal in a_candidate[PSDO.motivating_information]:
        for name in signals:
            try:
                signals[name] = round(
                    float(signal.value(getattr(SLOWMO, name)).value), 4
                )
            except Exception:
                pass

    return signals


def _matching_comparator(measure_identifier: str, comparator: Resource) -> pd.DataFrame:
    comparator_type = str(comparator.identifier)
    comparator_df = context.comparator_df
    comparator_period_start = pd.to_datetime(comparator_df["period.start"])
    performance_period_start = pd.to_datetime(context.performance_month)

    row_filter = (
        (comparator_df["measure"] == measure_identifier)
        & (comparator_period_start == performance_period_start)
        & (comparator_df["group.code"] == comparator_type)
    )

    merge_columns = startup.config.get("ComparatorMergeColumns", [])
    if not context.practitioner_role.empty:
        practitioner_role = context.practitioner_role.iloc[0]
        if "group.subject" in merge_columns:
            org_id = practitioner_role["PractitionerRole.organization"]
            row_filter &= comparator_df["group.subject"] == org_id
        if "PractitionerRole.code" in merge_columns:
            role = practitioner_role["PractitionerRole.code"]
            row_filter &= comparator_df["PractitionerRole.code"] == role

    comparator_filtered = comparator_df[row_filter]
    if len(comparator_filtered) != 1:
        raise ValueError(
            f"Expected exactly 1 comparator row, found {len(comparator_filtered)}"
        )

    return comparator_filtered


def build_communication_request(
    a_candidate: Resource, image: str = None, message_text: str = None
) -> dict:
    """
    Builds a CommunicationRequest for the selected candidate message.
    All values are derived from the candidate and graph, except the image
    and finalized message text, which Pictoralist generates separately.

    Parameters:
    - a_candidate (Resource): The selected candidate, or None if no candidate was selected.
    - image (str, optional): The base64-encoded graph image produced by Pictoralist, if any.
    - message_text (str, optional): The finalized message text produced by Pictoralist. Falls
      back to the candidate's raw template text if not provided.

    Returns:
    dict: A CommunicationRequest resource, or None if no candidate was selected.
    """
    if a_candidate is None:
        return None

    measure = a_candidate.value(SLOWMO.RegardingMeasure)
    measure_identifier = str(measure.identifier)

    communication_request = CommunicationRequest(
        identifier=f"communication-request-{context.subject}-{measure_identifier}",
        authored_on=datetime.datetime.now().isoformat(),
        subject_reference=f"Practitioner/{context.subject}",
    )

    nested = [
        CommunicationRequest.build_extension(
            "template_name", "valueString", str(a_candidate.value(SLOWMO.name))
        ),
        CommunicationRequest.build_extension(
            "template_id",
            "valueString",
            str(a_candidate.value(SLOWMO.AncestorTemplate)),
        ),
        CommunicationRequest.build_extension(
            "display", "valueString", str(a_candidate.value(SLOWMO.Display))
        ),
        CommunicationRequest.build_extension(
            "acceptable_by", "valueString", str(a_candidate.value(SLOWMO.AcceptableBy))
        ),
    ]
    selected_comparator = a_candidate.value(
        SLOWMO.RegardingComparator / SLOWMO.DisplayName
    )
    if selected_comparator is not None:
        nested.append(
            CommunicationRequest.build_extension(
                "selected_comparator", "valueString", str(selected_comparator)
            )
        )
    communication_request.add_extension(
        "https://umich.edu/scaffold/", extensions=nested
    )

    communication_request.add_extension(
        str(FHIR.improvementNotation),
        "valueString",
        value=measure.value(FHIR.improvementNotation).value,
    )

    # Add motivating signals
    signals = extract_motivating_signals(a_candidate)
    signal_value_keys = {
        "PerformanceGapSize": "valueDecimal",
        "PerformanceTrendSlope": "valueDecimal",
        "StreakLength": "valueInteger",
    }
    for name, value_key in signal_value_keys.items():
        if signals[name] is not None:
            communication_request.add_extension(
                str(getattr(SLOWMO, name)), value_key, value=signals[name]
            )

    communication_request.add_about(
        display=measure.value(FHIR.title).value,
        type="Measure",
        identifier_system="urn:ietf:rfc:3986",
        identifier_value=measure_identifier,
    )

    communication_request.add_text_payload(str(message_text))

    communication_request.add_attachment_payload(
        content_type="image/png",
        data=image,
    )

    # prepare performance measure reports
    performance_report_df = context.performance_df[
        (context.performance_df["measure"] == measure_identifier)
    ]
    performance_report_csv = performance_report_df.to_csv(index=False).encode("utf-8")

    communication_request.add_attachment_payload(
        content_type="text/csv; charset=utf-8",
        data=base64.b64encode(performance_report_csv).decode("ascii"),
        title="Performance measure reports",
    )

    # prepare the comparator measure report
    comparator = a_candidate.value(SLOWMO.RegardingComparator)
    if str(comparator) != "None":
        comparator_df = _matching_comparator(measure_identifier, comparator)
        comparator_report_csv = comparator_df.to_csv(index=False).encode("utf-8")

        communication_request.add_attachment_payload(
            content_type="text/csv; charset=utf-8",
            data=base64.b64encode(comparator_report_csv).decode("ascii"),
            title="Comparator measure reports",
        )

    return communication_request.to_json()


def load_kb_config(config_path: str) -> dict:
    try:
        with urlopen(config_path) as f:
            return yaml.safe_load(f.read().decode("utf-8"))

    except Exception as e:
        logger.error(f"Error loading knowledgebase config: {e}")


def load_esteemer(context):
    plugins = entry_points(group="scaffold.esteemer")

    for ep in plugins:
        if ep.name == startup.esteemer_plugin_name:
            cls = ep.load()
            obj = cls(context=context)

            if not isinstance(obj, Esteemer):
                raise TypeError(
                    f"{startup.esteemer_plugin_name} does not implement required select_candidate() method."
                )
            plugin_version = obj.version()

            if plugin_version != startup.esteemer_plugin_version:
                raise ValueError(
                    f"Plugin '{startup.esteemer_plugin_name}' version mismatch. "
                    f"Expected '{startup.esteemer_plugin_version}', "
                    f"found '{plugin_version}'."
                )

            return obj

    raise ValueError(f"Plugin '{startup.esteemer_plugin_name}' not found.")
