from models.chart import Song
from typing import List, Tuple, NamedTuple

#Aliases
GradeRatingTuple = Tuple[str,int]

#From Diving-Fish/maimaidx-prober
SCORE_COEFFICIENT_TABLE = [
    [0, 0, 'd'],
    [50, 8, 'c'],
    [60, 9.6, 'b'],
    [70, 11.2, 'bb'],
    [75, 12.0, 'bbb'],
    [80, 13.6, 'a'],
    [90, 15.2, 'aa'],
    [94, 16.8, 'aaa'],
    [97, 20, 's'],
    [98, 20.3, 'sp'],
    [99, 20.8, 'ss'],
    [99.5, 21.1, 'ssp'],
    [99.9999, 21.4, 'ssp'],
    [100, 21.6, 'sss'],
    [100.4999, 22.2, 'sss'],
    [100.5, 22.4, 'sssp']
]
UPSCORE_TABLE = [
    [97, 20, 's'],
    [99, 20.8, 'ss'],
    [100, 21.6, 'sss'],
    [100.5, 22.4, 'sssp']
]

class Score(NamedTuple):
    grade: str
    factor: float
    percent: float
            
class Record:
    def __init__(self, chart:Song, score:Score):
        self.chart = chart
        self.score = score
    
    def get_rating(self, diffLabel:str) -> int:
        return self.score.percent * self.score.factor * self.chart.difficulties[1]
    
    def get_possible_rating(self,diffLabel:str) -> List[GradeRatingTuple]:
        res = []
        for u_score in UPSCORE_TABLE:
            rating = UPSCORE_TABLE[0] * UPSCORE_TABLE[1] * self.chart.difficulties[1]
            res.append((UPSCORE_TABLE[2],rating))
        return res




