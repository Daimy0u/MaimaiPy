from typing import List, Tuple,NamedTuple
from enum import IntEnum
        
class DifficultyLabel:
    basic: int = 0
    advanced: int = 1
    expert: int = 2
    master: int = 3
    remaster: int = 4
    
    def get_label(self,id: int):
        return {0:"BASIC",1:"ADVANCED",2:"EXPERT",3:"MASTER",4:"Re:MASTER"}[id]
    
class DifficultyTuple(NamedTuple):
    difficulty_id: int
    internal: float
    external: str

class Song:
    def __init__(
            self,
            title: str = None,
            artist: str = None,
            category: str = None,
            bpm: int = -99,
            image_url: str = None
    ):
        self.title = title
        self.artist = artist
        self.category = category
        self.bpm = bpm
        self.image = image_url
        
        
class Chart:
    def __init__(
            self,
            title: str = None,
            artist: str = None,
            category: str = None,
            bpm: int = -99,
            image_url: str = None
    ):
        