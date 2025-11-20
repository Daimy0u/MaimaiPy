import pandas as pd
import numpy as np

from dataclasses import make_dataclass
from typing import Optional, Literal

from app.models.record import RecordCollection
Entry = make_dataclass("Entry", [('version_type',str),
                                 ('chart_type', str),
                                 ('difficulty', str),
                                 ('level_label', str),
                                 ('level_internal', float),
                                 ('achievement', float),
                                 ('rating', int),
                                 ('song_name', int)])

EntryColumn = Literal[
    "version_type",
    "chart_type",
    "difficulty",
    "level_label",
    "level_internal",
    "achievement",
    "rating",
    "song_name",
]

label_order = ['1', '2', '3', '4', '5', '6', '7', '8', '9', '9+', '10', '10+',
               '11', '11+', '12', '12+', '13', '13+', '14', '14+', '15']
class StatisticalCollection(RecordCollection):
    def __init__(self, record_collection: Optional[RecordCollection] = None):
        self._df: Optional[pd.DataFrame] = None
        if record_collection is not None:
            super().__init__()
            [self.add(r) for r in record_collection.entries]
        else:
            super().__init__()

    def as_dataframe(self, only_top_50: bool = False) -> pd.DataFrame:
        if only_top_50:
            new, old, _ = self.get_top_50()
            r_array = new[0] + old[0]
        else:
            r_array = self.entries
        dataclass_array = []
        for r in r_array:
            new_str = 'new' if r.is_new() else 'old'
            dataclass_array.append(Entry(new_str,
                                         r.chart_type,
                                         r.difficulty,
                                         r._lvl,
                                         r.internal_level,
                                         r.achievement_float,
                                         r.rating,
                                         r.song))
        df = pd.DataFrame(dataclass_array)
        df['level_label'] = pd.Categorical(df['level_label'], categories=label_order, ordered=True)
        return df






