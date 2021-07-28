"""
In charge of Serializing the data and calculating the deciles in order to calculate awesomness.
"""

import pandas as pd
import logging

logger = logging.getLogger(__name__)


class RatingCalculator(object):
    """
    Creates a data frame using all repo's data and calculate the awesome ratings for it.
    """

    RANKING_FIELDS = [('last_issue_date', "desc"),
                      ('issues_count', "asc"), ('forks_count', "desc"), ('stars', "desc")]
    DECILE_FORMAT = "{}_decile"
    SERIALIZEABLE_FIELDS = [("awesomeness", "Awesomeness"), ("description",
                                                             "Description"), ("license", "License"), ("url", "Link")]

    def __init__(self, repos):
        self._repos = repos
        self._data_frame = self.__create_decile_data_frame()

    def __create_decile_data_frame(self):
        """
        Creates a dataframe for all repos and calculates deciles for each ranking field

        :return: pandas data frame
        """

        data_frame = pd.DataFrame(self._repos)

        for field in RatingCalculator.RANKING_FIELDS:
            field_name = field[0]
            data_frame[RatingCalculator.DECILE_FORMAT.format(field_name)] = pd.qcut(
                data_frame[field_name].rank(method='first'), 10, labels=False)

        return data_frame

    def calculate_awesomeness(self):
        """
        Calculates the awesomeness according to the ranking fields order
        """

        logger.info("Calculating Awesomeness")
        scores = []
        for _, row in self._data_frame.iterrows():
            row_score = 0
            for ranking_field, ranking_order in RatingCalculator.RANKING_FIELDS:
                field_decile = row[RatingCalculator.DECILE_FORMAT.format(
                    ranking_field)]
                if ranking_order == 'asc':  # i.e Lower is better
                    row_score += 10 - field_decile
                if ranking_order == 'desc':
                    row_score += field_decile + 1
            scores.append(row_score)

        self._data_frame['awesomeness'] = scores

    def serialize(self):
        """
        Serialize the data frame to a dict according to serializeable fields

        :return: a list of dicts containing the serializeable fields
        """

        serialized_data = []
        for _, row in self._data_frame.iterrows():
            serialized_row = {}
            for field, display_name in RatingCalculator.SERIALIZEABLE_FIELDS:
                serialized_row[display_name] = row[field]

            serialized_data.append(serialized_row)

        return serialized_data
