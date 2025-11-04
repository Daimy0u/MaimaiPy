from typing import Any, Literal, Union, Final, Optional
from math import floor
MDXChartType = Literal['STD','DX']
MDXChartDifficulty = Literal['ReMASTER', 'MASTER', 'EXPERT', 'ADVANCED','BASIC']

SCORE_COEFFICIENT_TABLE: list[tuple[float,float,str]] = [
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
UPSCORE_TABLE = [
    [97, 20, 's'],
    [99, 20.8, 'ss'],
    [100, 21.6, 'sss'],
    [100.5, 22.4, 'sssp']
]

class RecordEntry:
    _type: MDXChartType
    _diff: MDXChartDifficulty
    data_source: dict = {}
    
    @classmethod
    def set_source(cls, source: dict):
        cls.data_source = source
        
    def __init__(self,
                 chart_type: MDXChartType, 
                 difficulty: MDXChartDifficulty, 
                 achievement: str, 
                 lvl: str, 
                 song: str
                 ):
        self._type = chart_type
        self._diff = difficulty
        self._achv = achievement
        self._lvl = lvl
        self._song = song
        
    @property   
    def achievement(self):
        return self._achv
    
    @property
    def achievement_float(self) -> float:
        res: float = 0.0
        try:
            res = float(self._achv[:-1])
        except (ValueError, TypeError): pass
        return res
    
    @property
    def song(self) -> str:
        return self._song
    
    @property
    def chart_type(self) -> MDXChartType:
        return self._type

    @property
    def difficulty(self) -> MDXChartDifficulty:
        return self._diff
    
    #TODO: Fetch internal constants from database
    @property
    def internal_level(self) -> float:
        name = self._song.strip()
        if name in RecordEntry.data_source:
            if self._type in RecordEntry.data_source[name]['constants']:
                if self._diff in RecordEntry.data_source[name]['constants'][self._type]:
                    return RecordEntry.data_source[name]['constants'][self._type][self._diff]
        res = 0.0
        if '+' in self._lvl:
            try:
                res = float(self._lvl[:-1]) + 0.7
            except:
                pass
        elif '?' in self._lvl:
            try:
                res = float(self._lvl[:-1])
            except:
                pass
        else:
            try:
                res = float(self._lvl)
            except:
                pass
        return res
            
    @property
    def rating(self) -> int:
        rating = 0
        for score,constant,rank in SCORE_COEFFICIENT_TABLE:
            if self.achievement_float > score:  
                curr = (self.achievement_float * (constant/100)) * self.internal_level
                if curr > rating: rating = curr
        return floor(rating)
    
    
    