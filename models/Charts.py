
class Difficulty:
    def __init__(self,constant:float,label:str):
        self.constant = constant
        self.label = label

class Chart:
    def __init__(
            self,
            title:str,
            difficulty: Difficulty,
            isDX: bool
    ):
        self.title = title
        self.difficulty = difficulty
        self.isDX = isDX