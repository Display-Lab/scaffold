import base64
import datetime
import io
import os
import sys

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from loguru import logger

from scaffold import context

## Logging setup
logger.remove()
logger.add(sys.stdout, colorize=True, format="{level} | {message}")


class Pictoralist:
    def __init__(
        self,
        performance_dataframe,
        selected_candidate,
        settings,
    ):
        ## Setup variables to process selected message
        # Needs cleanup to stop redundant var declaration (those passed directly to prepare_selected_message)
        self.performance_data = performance_dataframe  # Dataframe of recipient perf data (performance_data_df)

        # Need refactor
        self.selected_measure = str(
            selected_candidate["measure_name"]
        )  # Name of selected measure
        self.sel_measure_title = str(
            selected_candidate["measure_title"]
        )  # Formal name of measure
        self.template_id = str(
            selected_candidate["template_id"]
        )  # Message template ID of selected candidate message
        self.template_name = str(
            selected_candidate["template_name"]
        )  # Message template name
        self.display_format = str(
            selected_candidate["display"]
        )  # Selected display type
        self.message_text = str(
            selected_candidate["message_text"]
        )  # Raw message template fulltext (sans 'Additional message text' (changed 11/6))
        self.comparator_type = str(
            selected_candidate["comparator_type"]
        )  # ["Peer Top 25%", "Peer Top 10%", "Peer Average", "Goal Value"]
        self.acceptable_by = []  # Causal pathway determined to be acceptible by
        for pathway in selected_candidate["acceptable_by"]:
            self.acceptable_by.append(
                pathway
            )  # Add string value of rdflib literal to list
        self.base64_image = []  # Initialize as empty key to later fill image into

        # Config settings from main basesettings class
        self.log_level = settings.log_level
        self.generate_image = settings.generate_image
        self.cache_image = settings.cache_image
        self.display_timeframe = settings.display_window
        self.plot_goal_line = settings.plot_goal_line

        ## IMPLEMENTATION NEEDED ##
        # self.template_name      = str(selected_candidate["template_name"])  # Template text name
        # Semantic name of message template, would be best to implement much earlier in the pipeline, carry it forward

    # # # # # # # # # # # # Data Setup and Manipulations # # # # # # # # # # # # #

    ### Clean dataframe of non-selected performance data for graph generation, reason on comparator message is about, and make changes to set up graphing
    def prep_data_for_graphing(self):
        ## Initial dataframe shape:
        # staff_number, measure, month, passed_count, flagged_count, denominator, peer comparators (x3), MPOG_goal, Performance_Rate, comparator_level

        # Only keep rows that contain the measure of interest for this message:
        self.performance_data = self.performance_data[
            self.performance_data["measure"] == self.selected_measure
        ]

        self.performance_data = self.performance_data.copy()

        # # Initialize new column of data to store only this feedback's crucial comparator levels for graphing as a float:
        self.performance_data.loc[:, "comparator_level"] = (
            0.0000  # initialize column as float
        )
        self.performance_data.loc[:, "goal_percent"] = 0.0000  # same as above

        ## Change processing and graphing depending on comparator type:
        # Make changes based on peer 50th percentile benchmark being comparator message "is about"
        if self.comparator_type == "Peer Average":
            self.performance_data["comparator_level"] = self.performance_data[
                "peer_average_comparator"
            ]  # Select which column of data to keep as the 'comparator_level'

        # Same as above, but for peer 75th percentile benchmark
        elif self.comparator_type == "Peer Top 25%":
            self.performance_data["comparator_level"] = self.performance_data[
                "peer_75th_percentile_benchmark"
            ]

        # Same as above, but for peer 90th percentile benchmark
        elif self.comparator_type == "Peer Top 10%":
            self.performance_data["comparator_level"] = self.performance_data[
                "peer_90th_percentile_benchmark"
            ]

        # Same as above, but for goal comparator messages
        else:
            self.performance_data["comparator_level"] = self.performance_data[
                "MPOG_goal"
            ]

        ## Convert values in selected columns for further processing:
        self.performance_data["month"] = pd.to_datetime(
            self.performance_data["month"]
        )  # convert month column to datetime objects
        self.performance_data["performance_level"] = (
            self.performance_data["passed_count"]
            / self.performance_data["denominator"]
            * 100.0
        )  # convert preformance ratio to percentage
        self.performance_data["goal_percent"] = self.performance_data[
            "MPOG_goal"
        ]  # convert MPOG goal ratio to percentage

        ## Drop extraneous columns of current dataframe
        cols_to_keep = [
            "month",
            "measure",
            "passed_count",
            "denominator",
            "performance_level",
            "comparator_level",
            "goal_percent",
        ]
        self.performance_data = self.performance_data[cols_to_keep]

    ### Fill data voids in the dataset
    def fill_missing_months(self):
        ## Sort the DataFrame by the 'month' column
        self.performance_data = self.performance_data.sort_values(by="month")

        ## Create a date range for all months between the earliest and latest month
        start_date = self.performance_data["month"].min()
        end_date = self.performance_data["month"].max()
        all_months = pd.date_range(start_date, end_date, freq="MS")

        if len(all_months) != len(self.performance_data["month"]):
            logger.info("Data gap(s) detected, filling voids...")

            # Reindex the DataFrame with all months and fill missing values
            self.performance_data = (
                self.performance_data.set_index("month")
                .reindex(all_months, fill_value=None)
                .reset_index()
            )
            self.performance_data = self.performance_data.rename(
                columns={"index": "month"}
            )  # reset col name from index to month

            # Forward fill 'measure' and percent-scale version of 'MPOG_goal' columns with the previous valid values
            self.performance_data["measure"] = self.performance_data["measure"].ffill()
            self.performance_data["goal_percent"] = self.performance_data[
                "goal_percent"
            ].ffill()

            # Debugging statement
            # logger.debug(f"After gap fill, dataframe is:")
            # logger.debug(f'\n{self.performance_data}')

    ### Logic to set display timeframe for graph generation
    def set_timeframe(self):
        available_timeframe = len(self.performance_data)
        logger.debug(
            f"Requested {self.display_timeframe} month display, dataframe has {len(self.performance_data)} months"
        )

        ## Restrict graph to extant data if less than user-set default
        if self.display_timeframe > available_timeframe:
            logger.debug("Restricting time window due to lack of data")
            self.display_timeframe = available_timeframe

        ## Error catcher for windows <3 months
        if self.display_timeframe < 3:
            self.generate_image = False  # Turn off image generation
            self.display_format = "text only"  # Set to text-only display type
            logger.warning("Dataset too small, display format forced to text only")
            logger.debug(
                f"Display Format: {self.display_format}\tDisplay Months: {self.display_timeframe}"
            )
            logger.debug(f"Performance dataframe is:\n{self.performance_data}")

    ### Fill template text with details for this month's precision feedback message
    def finalize_text(self):
        ## Pull the most recent month's data for generating text feedback:
        current_comparator_percent = self.performance_data["comparator_level"].iloc[-1]
        current_perf_percent = self.performance_data["performance_level"].iloc[-1]
        current_perf_passed = self.performance_data["passed_count"].iloc[-1]
        current_perf_total_cases = self.performance_data["denominator"].iloc[-1]
        self.init_time = datetime.datetime.now()  # Log time when text gen starts

        ## Replace placeholders in the template with actual values:
        # Format "[measure name]":
        self.message_text = self.message_text.replace(
            "[measure name]",
            f"{self.sel_measure_title}",
        )
        # Format "[recipient performance level]":
        self.message_text = self.message_text.replace(
            "[recipient performance level]",
            f"{current_perf_percent:.1f}% ({current_perf_passed}/{current_perf_total_cases} cases)",
        )
        # Format "[comparator performance level]":
        self.message_text = self.message_text.replace(
            "[comparator performance level]", f"{current_comparator_percent:.1f}%"
        )
        ## Insert framework for linking to MPOG measure spec and dashboard link here if task ownership changes

    # # # # # # # # # # # Graphing Functions # # # # # # # # # # # # # #

    ### Modularized plotting and saving shared code for both visual display types:
    def plot_and_save(self):
        logger.debug("Running 'plot_and_save'...")
        plt.tight_layout()
        plt.gca().set_alpha(
            0
        )  # Set alpha channel level to 0, full transparency of current axes
        # plt.show()  # Allow for spot-check of graph locally (not for production)

        ## Image cacheing functional code:
        if self.cache_image:
            # Specify cache folder name and image filename
            folderName = "pictoralist_cache"
            os.makedirs(folderName, exist_ok=True)
            imgName = os.path.join(folderName, f"response_{self.init_time}.png")

            # Save figure to cache, then save to io bytes object, convert to base64 and return
            plt.savefig(imgName, dpi=300, bbox_inches="tight")  # Save figure locally

        ## Save figure to io bytes object, encode base64, and return:
        s = io.BytesIO()
        plt.savefig(s, format="png", dpi=300, bbox_inches="tight")
        plt.close()
        s = base64.b64encode(s.getvalue()).decode("utf-8").replace("\n", "")
        return s

    ### Function to generate line chart
    def generate_linegraph(self):
        ## Define the axes, values, and their labels
        y_values = np.arange(0, 101, 20)
        y_labels = [str(val) + "%" for val in y_values]
        x_values = self.performance_data["month"][
            -self.display_timeframe :
        ].dt.strftime("%b '%y")
        plt.figure(figsize=(5, 2.5))  # Create the plot

        ## Restrict graph to timeframe specified by set_timeframe()
        perf_series = self.performance_data["performance_level"][
            -self.display_timeframe :
        ]
        comp_series = self.performance_data["comparator_level"][
            -self.display_timeframe :
        ]

        ## Add vertical lines for each month
        for x in x_values:
            plt.axvline(x=x, color="gray", linewidth=0.3)

        ## Plot performance and comparator level series
        plt.plot(
            x_values,
            perf_series,
            label="You",
            color="#063763",
            linewidth=1.2,
            marker=".",
        )
        plt.plot(
            x_values,
            comp_series,
            label=self.comparator_type,
            color="#02b5af",
            linewidth=1.0,
            marker=".",
        )

        ## Add month labels to x axis
        plt.xticks(fontsize=7)

        ## Set Axes and plot labels
        plt.yticks(y_values, y_labels, fontsize=7)
        # Requested removal of labels, may implement again in debug for spot checking images
        # plt.ylabel("Performance Level", weight='bold', fontsize=5)
        # plt.xlabel("Time", weight='bold', fontsize=5)
        # plt.title(f"Performance Over Time for Measure {self.selected_measure}", weight='bold', fontsize=5)

        ## Add data labels for the last three months of performance levels as floats
        last_three_months = x_values[-3:]
        last_three_performance = self.performance_data["performance_level"][-3:]
        last_three_passed = self.performance_data["passed_count"][-3:]
        last_three_denom = self.performance_data["denominator"][-3:]

        for month, performance, passed, denom in zip(
            last_three_months,
            last_three_performance,
            last_three_passed,
            last_three_denom,
        ):
            label_text = f"{performance:.0f}%\n{passed} / {denom}"

            ## Adjust the xytext parameter to move the label conditionally
            vert_offset = -15
            if performance < 25:
                vert_offset = 15

            plt.annotate(
                label_text,
                (month, performance),
                textcoords="offset points",
                weight="bold",
                xytext=(0, vert_offset),  # Offset adjusted conditionally
                ha="center",
                fontsize=5,
                color="#063763",
            )

        plt.legend(
            loc="lower center",
            bbox_to_anchor=(0.5, -0.3),
            ncol=2,
            fontsize=6,
            frameon=False,
        )

        ## Save and display the graph
        self.base64_image = self.plot_and_save()

    ### Function to generate bar chart
    def generate_barchart(self):
        plt.figure(figsize=(5, 2.5))  # Create figure instance (500x250 @ 300dpi)
        bar_width = 0.45  # Arbitrary bar width, adjust to find a good ratio to the display window
        bar_spacing = 0

        ## Define the axes, values, and labels
        y_values = np.arange(0, 101, 20)
        y_labels = [str(val) + "%" for val in y_values]
        x_values = self.performance_data["month"][
            -self.display_timeframe :
        ].dt.strftime("%b '%y")

        ## Create bars for the timeframe specified by set_timeframe()
        graphed_perf = self.performance_data["performance_level"][
            -self.display_timeframe :
        ]
        graphed_comp = self.performance_data["comparator_level"][
            -self.display_timeframe :
        ]
        graphed_pass = self.performance_data["passed_count"][-self.display_timeframe :]
        graphed_denom = self.performance_data["denominator"][-self.display_timeframe :]

        ## If include_goal_line is True, plot the goal line
        if self.plot_goal_line and self.comparator_type != "Goal Value":
            plt.hlines(
                y=self.performance_data["goal_percent"][
                    -self.display_timeframe :
                ].values,
                xmin=0,
                xmax=len(x_values),
                linestyle="--",
                color="black",
                label="Goal",
                linewidth=0.5,
            )

        ## Plot the bars for both data series
        x1 = np.arange(len(x_values)) + bar_width / 2  # position for first bar
        x2 = [x + bar_width + bar_spacing for x in x1]  # position for second bar
        plt.bar(x1, graphed_perf, width=bar_width, label="You", color="#00254a")
        plt.bar(
            x2,
            graphed_comp,
            width=bar_width,
            label=self.comparator_type,
            color="#4d5458",
        )

        ## Add data labels for each bar in performance levels
        for month, performance, passed, denom in zip(
            x1, graphed_perf, graphed_pass, graphed_denom
        ):
            if not np.isnan(performance):
                label_text = f"{performance:.0f}%\n{passed} / {denom}"

                # Create and adjust annotations (and text color)
                vert_offset = -15
                text_color = "#ffffff"
                if performance < 25:
                    vert_offset = 15
                    text_color = "#00254a"

                plt.annotate(
                    label_text,
                    (month, performance),
                    ha="center",
                    va="bottom",
                    fontsize=4.5,
                    color=text_color,
                    xytext=(-(bar_width / 2), vert_offset),  # Trying variable offset
                    textcoords="offset points",
                    weight="bold",
                )

        ## Add data labels for each bar in comparator levels
        for month, comparator, passed, denom in zip(
            x2, graphed_comp, graphed_pass, graphed_denom
        ):
            if not np.isnan(comparator):
                label_text = f"{comparator:.0f}"

                # Create and adjust annotations
                vert_offset = -20
                text_color = "#ffffff"
                if comparator < 25:
                    vert_offset = 20
                    text_color = "#000000"

                plt.annotate(
                    label_text,
                    (month, comparator),
                    ha="center",
                    va="bottom",
                    fontsize=5,
                    color="#f3f0ed",
                    xytext=(
                        -(bar_width / 2),
                        vert_offset,
                    ),  # Variable offest for comparators as well
                    textcoords="offset points",
                    weight="bold",
                )

        ## Configure labels, titles, ticks, and limits
        plt.yticks(y_values, y_labels, fontsize=7)
        plt.xticks(x1 + bar_width / 2, x_values, fontsize=7)
        plt.ylim(0, 100)
        # plt.title(f"Performance Over Time for Measure {self.selected_measure}", weight='bold', fontsize=5)
        # plt.xlabel("Time", weight='bold', fontsize=5)
        # plt.ylabel("Performance Level", weight='bold', fontsize=5)

        ## Format legend and grid
        plt.legend(
            loc="lower center",
            bbox_to_anchor=(0.5, -0.3),
            ncol=3,
            fontsize=6,
            frameon=False,
        )
        plt.grid(False)

        ## Save and display the graph
        self.base64_image = self.plot_and_save()

    ### Graphing function control logic (modularized to allow for changes and extra display formats in the future):
    def graph_controller(self):
        if self.display_format == "line chart" and self.generate_image:
            logger.info("Generating line chart from performance data...")
            self.generate_linegraph()

        elif self.display_format == "bar chart" and self.generate_image:
            logger.info("Generating bar chart from performance data...")
            self.generate_barchart()

        else:
            logger.info("Generating text only feedback message, graphing skipped...")

    ### Prepare selected message as done previously for LDT continuity:
    def prepare_selected_message(self):
        logger.debug("Running pictoralist/prepare_selected_message...")
        candidate = {}
        message = {}
        candidate["message_template_id"] = self.template_id
        candidate["message_template_name"] = self.template_name
        candidate["display"] = self.display_format
        candidate["measure"] = self.selected_measure
        candidate["acceptable_by"] = self.acceptable_by
        message["text_message"] = self.message_text
        message["measure"] = self.selected_measure
        message["measure_full_title"] = self.sel_measure_title
        # message["message_addtl_text"]       =self.template_addtl_text  # Ditto
        message["image"] = self.base64_image

        full_message = {
            "pfkb_version": "0.0.0",  # Need to soft code this so it is accurate
            "pfp_version": "0.2.1",  # Ditto
            "staff_number": context.staff_number,
            "selected_candidate": candidate,
            "selected_comparator": self.comparator_type,
            "performance_month": self.performance_data["month"]
            .iloc[-1]
            .strftime("%B %Y"),  # Becomes string in response, format here
            "message_generated_datetime": self.init_time,
            "message": message,
        }

        return full_message
