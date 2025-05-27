import sqlite3 as sql
from abc import abstractmethod,ABC

##TODO
class Database(ABC):
    """
    Abstract base class. Subclasses set `db_name` and implement `configure()`.
    """
    db_name: str
    connection: sql.Connection
    cursor: sql.Cursor

    def __init__(self):
        # Open (or create) the DB file
        self.connection = sql.connect(self.db_name)
        # Allow name-based access to columns
        self.connection.row_factory = sql.Row
        self.cursor = self.connection.cursor()
        # Let subclass create its tables
        self.configure()
        # Persist DDL
        self.connection.commit()

    @abstractmethod
    def configure(self):
        """CREATE TABLE IF NOT EXISTS …"""
        ...

class MusicDB(Database):
    db_name = 'music.db'
    
    def configure(self):
        # Song table: one row per track
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS song (
                id           INTEGER PRIMARY KEY,
                title        TEXT    NOT NULL,
                artist       TEXT,
                category     INTEGER NOT NULL,
                version      TEXT    NOT NULL,
                region       TEXT    NOT NULL,
                release_date  TEXT,
                image_url    TEXT
            );
        """)

        # Chart table: one row per difficulty/type variant
        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS chart (
            id                   INTEGER PRIMARY KEY AUTOINCREMENT,
            song_id              INTEGER NOT NULL,   -- FK
            type                 TEXT    NOT NULL,   -- plaintext chart type
            difficulty_label     TEXT    NOT NULL,   -- DifficultyTuple.label
            difficulty_internal  REAL,   -- DifficultyTuple.internal
            difficulty_external  TEXT    NOT NULL,   -- DifficultyTuple.external
            FOREIGN KEY(song_id) REFERENCES song(id)
        )
        """)
    
    
        