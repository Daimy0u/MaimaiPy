"""Provides classes for play record entries."""

from functools import lru_cache
from math import floor
from json import dumps as jsonDump
from app.types.maimaidx import *
from app.core.datasource import MDXDataSource

SCORE_COEFFICIENT_TABLE: list[tuple[MDXRecordAchievementFloat,MDXGameCoefficient,MDXRecordRank]] = [
    (0, 0, 'd'),
    (50, 8, 'c'),
    (60, 9.6, 'b'),
    (70, 11.2, 'bb'),
    (75, 12.0, 'bbb'),
    (80, 13.6, 'a'),
    (90, 15.2, 'aa'),
    (94, 16.8, 'aaa'),
    (97, 20, 's'),
    (98, 20.3, 'sp'),
    (99, 20.8, 'ss'),
    (99.5, 21.1, 'ssp'),
    (99.9999, 21.4, 'ssp'),
    (100, 21.6, 'sss'),
    (100.4999, 22.2, 'sss'),
    (100.5, 22.4, 'sssp')
]

@lru_cache
def _cached_calculation(coefficient: float, constant: float) -> float:
    return (coefficient / 100) * constant



class RecordEntry:
    """
    MaimaiDX record entry class

    Call RecordEntry.set_source(source: MDXDataSource) to use external sources for constants.

    Defaults to floor-rounding based on label (e.g. 14+ -> 14.7)
    """
    _type: MDXChartType
    _diff: MDXChartDifficulty
    data_source: MDXDataSource

    @classmethod
    def set_source(cls, source: MDXDataSource):
        """
        Directs all RecordEntry instances to use source.
        """
        cls.data_source = source

    def __init__(self,
                 chart_type: MDXChartType,
                 difficulty: MDXChartDifficulty,
                 achievement: MDXRecordAchievement,
                 lvl: MDXChartLevel,
                 song: MDXSongName,
                 sync: MDXRecordSync,
                 combo: MDXRecordCombo
                 ):
        """Initialises internal class variables."""
        self._type: MDXChartType = chart_type
        self._diff: MDXChartDifficulty = difficulty
        self._achv: MDXRecordAchievement = achievement
        self._lvl: MDXChartLevel = lvl
        self._song: MDXSongName = song
        self._sync: MDXRecordSync= sync
        self._combo: MDXRecordCombo = combo

        # external datasource status
        self._fetched = False

    @property
    def achievement(self):
        """Achievement String"""
        return self._achv

    @property
    def achievement_float(self) -> MDXRecordAchievementFloat:
        """Achievement Float"""
        res: float = 0.0
        try:
            res = float(self._achv[:-1])
        except (ValueError, TypeError): pass
        return res

    @property
    def song(self) -> MDXSongName:
        """Song Name"""
        return self._song

    @property
    def chart_type(self) -> MDXChartType:
        """Chart Type (DX/STD)"""
        return self._type

    @property
    def difficulty(self) -> MDXChartDifficulty:
        """Difficulty"""
        return self._diff

    @property
    def combo(self) -> MDXRecordCombo:
        """Combo Label e.g. fc,fcp,fdx"""
        return self._combo

    @property
    def sync(self) -> MDXRecordSync:
        """Sync label e.g. fs,fsp"""
        return self._sync

    @property
    def internal_level(self) -> MDXChartInternal:
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
    def rating(self) -> MDXRecordRating:
        """
        Rating calculated from constants and self.internal_level property method.
        """
        rating = 0
        for score,constant,rank in SCORE_COEFFICIENT_TABLE:
            if self.achievement_float >= score:
                curr = self.achievement_float * _cached_calculation(constant, self.internal_level)
                if curr > rating:
                    rating = curr
        return floor(rating)

    @property
    def rank(self) -> MDXRecordRank:
        result_rank: MDXRecordRank = 'd'
        for score,_,rank in SCORE_COEFFICIENT_TABLE:
            if self.achievement_float >= score:
                result_rank = rank
        return result_rank


    @property
    def valid(self) -> bool:
        sheet = None
        if RecordEntry.data_source:
            sheet = RecordEntry.data_source.get_sheet(self.song,
                                                      self.chart_type,
                                                      self.difficulty)
        return sheet is not None


    #String Helpers
    def __repr__(self) -> str:
        str_json = {"key": [self.song,
                            self.chart_type,
                            self.difficulty],

                    "meta": [self.internal_level,
                             self.data_source.__name__ if self._fetched else 'Guessing'],

                    "sourced": self.valid,

                    "record": [round(self.achievement_float, 4),
                               self.rank,
                               self.combo,
                               self.sync],

                    "rating": self.rating
                    }


        return jsonDump(str_json, ensure_ascii=False)






