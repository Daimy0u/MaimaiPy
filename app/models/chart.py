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
    title = db.Column("title", db.Text, primary_key=True)
    title_kana = db.Column("title_kana", db.Text, )
    artist_name = db.Column("artist", db.Text)
    category = db.Column("category", db.String(30))
    bpm = db.Column("bpm", db.Integer)
    genre = db.Column("genre", db.Text)
    image_url = db.Column("image_url", db.String(255))
        
class Chart:
    pass
        