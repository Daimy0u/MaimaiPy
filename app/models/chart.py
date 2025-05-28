from typing import List, Tuple,NamedTuple
from enum import IntEnum
from . import db, BaseModel
class DifficultyLabel(IntEnum):
    BASIC = 0
    ADVANCED = 1
    EXPERT = 2
    MASTER = 3
    REMASTER = 4
    
class DifficultyTuple(NamedTuple):
    difficulty_id: int
    internal: float
    external: str

class Song(BaseModel):
    song_id = db.Column("id", db.Integer, primary_key=True)
    title = db.Column("title", db.Text)
    artist_name = db.Column("artist", db.Text, db.ForeignKey("artist.name"))
    category = db.Column("category", db.String(30))
    bpm = db.Column("bpm", db.Integer)
    image_url = db.Column("image_url", db.String(255))

class Artist(BaseModel):
    name = db.Column("name", db.String(50))
        
class Chart:
    def __init__(
            self,
            title: str = None,
            artist: str = None,
            category: str = None,
            bpm: int = -99,
            image_url: str = None
    ):
        