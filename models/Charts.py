from typing import List, Tuple

class Difficulty:
    """
    Compiles all difficulty in a dictionary for every chart.

    Args:
        diffList (List) [
            label (str) - "Expert", "Master", etc.
            
            lvl (int) - Rounded Level Label
            
            constant (float | None) - Chart Constant
        ]
    """
    def __init__(self,diffList:List[Tuple[str,int,float | None]]):
        self.data = {}
        for diff in diffList:
            self.data[diff[0]] = {
                'lvl':diff[1],
                'constant':diff[2]
            }


class Chart:
    def __init__(
            self,
            title:str,
            difficulties: Difficulty,
            imageUrl: str | None
    ):
        self.title = title
        self.difficulties = difficulties
        self.image = imageUrl

class ChartContainer:
    def __init__(self,gameVersion : str):
        self.version = gameVersion
        self.data = {}

    def addChart(self,chart:Chart):
        self.data[chart.title] = chart
    
    def storeData(self):
        #TODO: Save Chart Data to JSON
        return