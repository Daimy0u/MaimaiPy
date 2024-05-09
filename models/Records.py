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

class Score:
    def __init__(self, recordPercent):
        for i in range(len(SCORE_COEFFICIENT_TABLE)):
            if i == len(SCORE_COEFFICIENT_TABLE) - 1 or recordPercent < SCORE_COEFFICIENT_TABLE[i + 1][0]:
                self.grade = SCORE_COEFFICIENT_TABLE[i][2]
                self.constant = SCORE_COEFFICIENT_TABLE[i][1]
                self.percent = SCORE_COEFFICIENT_TABLE[i][0]
                return
