from . import db, BaseModel

class Game(BaseModel):
    game_id = db.Column("id", db.Integer, primary_key=True) #Is there a std set of IDs? TODO
    name = db.Column("name", db.Text)

class Version(BaseModel):
    version_id = db.Column("id", db.Integer, primary_key=True)
    version_name = db.Column("name", db.Text)
    release_date = db.Column("release_date", db.DateTime, nullable=True)
    version_logo_url = db.Column("image_url", db.String(100), nullable=True)

class Region(BaseModel):
    region_id = db.Column("id", db.Integer, primary_key=True)
    game_id = db.Column("game_id", db.Integer, db.ForeignKey("game.id"))
    region_name = db.Column("name", db.String(20))
    