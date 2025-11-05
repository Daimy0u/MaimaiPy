from math import floor
from app.data_types.maimaidx import *
from app.datasource import MDXDataSource
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
UPSCORE_TABLE = [
    [97, 20, 's'],
    [99, 20.8, 'ss'],
    [100, 21.6, 'sss'],
    [100.5, 22.4, 'sssp']
]

class RecordEntry:
    _type: MDXChartType
    _diff: MDXChartDifficulty
    data_source: MDXDataSource
    
    @classmethod
    def set_source(cls, source: MDXDataSource):
        cls.data_source = source
        
    def __init__(self,
                 chart_type: MDXChartType, 
                 difficulty: MDXChartDifficulty, 
                 achievement: MDXRecordAchievement, 
                 lvl: MDXChartLevel, 
                 song: MDXSongName
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
    def achievement_float(self) -> MDXRecordAchievementFloat:
        res: float = 0.0
        try:
            res = float(self._achv[:-1])
        except (ValueError, TypeError): pass
        return res
    
    @property
    def song(self) -> MDXSongName:
        return self._song
    
    @property
    def chart_type(self) -> MDXChartType:
        return self._type

    @property
    def difficulty(self) -> MDXChartDifficulty:
        return self._diff
    
    #TODO: Fetch internal constants from database
    @property
    def internal_level(self) -> MDXChartInternal:
        song_name = self._song.strip()
        res = RecordEntry.data_source.get_constant(song_name=song_name,chart_type=self._type,difficulty=self._diff)
        if isinstance(res, float):
            if res > 0.0: return res
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
        rating = 0
        for score,constant,rank in SCORE_COEFFICIENT_TABLE:
            if self.achievement_float >= score:  
                curr = (self.achievement_float * (constant/100)) * self.internal_level
                if curr > rating: rating = curr
        return floor(rating)
    
    
    