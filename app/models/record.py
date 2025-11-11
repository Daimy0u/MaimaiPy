"""Provides classes for play record entries."""

from functools import lru_cache
from math import floor
from json import dumps as jsonDump

from app.core.datasource.base import MDXDataSource
from app.core.games.maimaidx import MaimaiDX

def _is_current(stringable: str | int | float | None) -> bool:
    if not isinstance(stringable, str):
        stringable = str(stringable)

    return stringable.strip().upper() in MaimaiDX.VERSION_EX

@lru_cache
def _cached_calculation(coefficient: float, constant: float) -> float:
    return (coefficient / 100) * constant



class RecordEntry:
    """
    MaimaiDX record entry class

    Call RecordEntry.set_source(source: MDXDataSource) to use external sources for constants.

    Defaults to floor-rounding based on label (e.g. 14+ -> 14.7)
    """
    _type: MaimaiDX.ChartType
    _diff: MaimaiDX.ChartDifficulty
    data_source: MDXDataSource

    @classmethod
    def set_source(cls, source: MDXDataSource):
        """
        Directs all RecordEntry instances to use source.
        """
        cls.data_source = source

    def __init__(self,
                 chart_type: MaimaiDX.ChartType,
                 difficulty: MaimaiDX.ChartDifficulty,
                 achievement: MaimaiDX.RecordAchievement,
                 lvl: MaimaiDX.ChartLevel,
                 song: MaimaiDX.SongName,
                 sync: MaimaiDX.RecordSync,
                 combo: MaimaiDX.RecordCombo
                 ):
        """Initialises internal class variables."""
        self._type: MaimaiDX.ChartType = chart_type
        self._diff: MaimaiDX.ChartDifficulty = difficulty
        self._achv: MaimaiDX.RecordAchievement = achievement
        self._lvl: MaimaiDX.ChartLevel = lvl
        self._song: MaimaiDX.SongName = song
        self._sync: MaimaiDX.RecordSync= sync
        self._combo: MaimaiDX.RecordCombo = combo

        # external datasource status
        self._fetched = False

    @property
    def achievement(self):
        """Achievement String"""
        return self._achv

    @property
    def achievement_float(self) -> MaimaiDX.RecordAchievementFloat:
        """Achievement Float"""
        res: float = 0.0
        try:
            res = float(self._achv[:-1])
        except (ValueError, TypeError): pass
        return res

    @property
    def song(self) -> MaimaiDX.SongName:
        """Song Name"""
        return self._song

    @property
    def chart_type(self) -> MaimaiDX.ChartType:
        """Chart Type (DX/STD)"""
        return self._type

    @property
    def difficulty(self) -> MaimaiDX.ChartDifficulty:
        """Difficulty"""
        return self._diff

    @property
    def combo(self) -> MaimaiDX.RecordCombo:
        """Combo Label e.g. fc,fcp,fdx"""
        return self._combo

    @property
    def sync(self) -> MaimaiDX.RecordSync:
        """Sync label e.g. fs,fsp"""
        return self._sync

    @property
    def internal_level(self) -> MaimaiDX.ChartInternal:
        """
        Internal constant of chart.

        Fetches from source if set, or lower-bound guess from level label.
        """
        song_name = self._song.strip()
        res = RecordEntry.data_source.get_constant(song_name=song_name,chart_type=self._type,difficulty=self._diff)
        if isinstance(res, float):
            if res > 0.0:
                self._fetched = True
                return res
        elif not res:
            #try again, see if it is resolved
            res = RecordEntry.data_source.get_constant(song_name=song_name,chart_type=self._type,difficulty=self._diff)

            res = 0.0
        else:
            raise ValueError("get_constant with parameters returned map, voodoo magic going on!")

        if '+' in self._lvl:
            try:
                res = float(self._lvl[:-1]) + 0.7
            except (ValueError, TypeError):
                pass
        elif '?' in self._lvl:
            try:
                res = float(self._lvl[:-1])
            except (ValueError, TypeError):
                pass
        else:
            try:
                res = float(self._lvl)
            except (ValueError, TypeError):
                pass
        return res

    @property
    def rating(self) -> MaimaiDX.RecordRating:
        """
        Rating calculated from constants and self.internal_level property method.
        """
        rating = 0
        for score,constant,rank in MaimaiDX.SCORE_COEFFICIENT_TABLE:
            if self.achievement_float >= score:
                achv = 0.0
                if self.achievement_float <= 100.5:
                    achv = self.achievement_float
                else:
                    achv = 100.5
                curr = achv * _cached_calculation(constant, self.internal_level)
                if curr > rating:
                    rating = curr
        return floor(rating)

    @property
    def rank(self) -> MaimaiDX.RecordRank:
        result_rank: MaimaiDX.RecordRank = 'd'
        for score,_,rank in MaimaiDX.SCORE_COEFFICIENT_TABLE:
            if self.achievement_float >= score:
                result_rank = rank
        return result_rank

    def is_new(self) -> bool:
        if not RecordEntry.data_source:
            return False

        version = RecordEntry.data_source.get_song_version(song_name=self._song)
        return _is_current(version)

    @property
    def valid(self) -> bool:
        sheet = None
        if RecordEntry.data_source:
            sheet = RecordEntry.data_source.get_sheet(self.song,
                                                      self.chart_type,
                                                      self.difficulty)
        return sheet is not None

    def as_dict(self):
        """
        Convert the record object to a dictionary representation.

        Returns:
            dict: A dictionary containing the following keys:
                - key (list): A list containing [song, chart_type, difficulty]
                - meta (list): A list containing [internal_level, data_source_name or None]
                - sourced (bool): Indicates whether the record has valid data
                - record (list): A list containing [achievement_float (rounded to 4 decimals), rank, combo, sync]
                - rating: The calculated rating value for this record
        """
        return {"key": [self.song,
                self.chart_type,
                self.difficulty],

                "meta": [self.internal_level,
                         self.data_source.__name__ if self._fetched else None],

                "sourced": self.valid,

                "record": [round(self.achievement_float, 4),
                           self.rank,
                           self.combo,
                           self.sync],

                "rating": self.rating
                }
    #String Helpers
    def __repr__(self) -> str:
        return jsonDump(self.as_dict(), ensure_ascii=False)






