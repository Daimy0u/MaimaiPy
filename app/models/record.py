"""Provides classes for play record entries."""

from functools import lru_cache
from math import floor
from json import dumps as json_dump
from json import loads as json_load
from logging import Logger
from typing import Any, Optional, Literal

from app.core.utils.log import Logged
from app.core.datasource.base import MDXDataSource
from app.core.games.maimaidx import MaimaiDX

def _is_current(stringable: str | int | float | None) -> bool:
    if not isinstance(stringable, str):
        stringable = str(stringable)

    return stringable.strip().upper() in MaimaiDX.VERSION_EX

@lru_cache
def _cached_calculation(coefficient: float, constant: float) -> float:
    return (coefficient / 100) * constant

ScoreDifference = float

class RecordEntry(Logged):
    """
    MaimaiDX record entry class

    Call RecordEntry.set_source(source: MDXDataSource) to use external sources for constants.

    Defaults to floor-rounding based on label (e.g. 14+ -> 14.7)
    """
    _type: MaimaiDX.ChartType
    _diff: MaimaiDX.ChartDifficulty
    data_source: MDXDataSource

    @classmethod
    def set_source(cls, source: MDXDataSource):
        """
        Directs all RecordEntry instances to use source.
        """
        cls.data_source = source

    def __init__(self,
                 song: Optional[MaimaiDX.SongName] = None,
                 chart_type: Optional[MaimaiDX.ChartType] = None,
                 difficulty: Optional[MaimaiDX.ChartDifficulty] = None,
                 achievement: Optional[MaimaiDX.RecordAchievement] = None,
                 lvl: Optional[MaimaiDX.ChartLevel] = None,
                 sync: Optional[MaimaiDX.RecordSync] = None,
                 combo: Optional[MaimaiDX.RecordCombo] = None,
                 import_str: Optional[str] = None,
                 import_dict: Optional[dict] = None
                 ):
        """Initialises internal class variables."""
        self._fetched = False
        if import_str:
            if self.from_str(import_str):
                 return
            else:
                del self
                return
        if import_dict:
            if self.from_dict(import_dict):
                return
            else:
                del self
                return

        if song and chart_type and difficulty and achievement:
            self._song: MaimaiDX.SongName = song
            self._type: MaimaiDX.ChartType = chart_type
            self._diff: MaimaiDX.ChartDifficulty = difficulty
            self._achv: MaimaiDX.RecordAchievement = achievement
        else:
            missing = [p for p in [song, chart_type, difficulty, achievement] if p is None]
            self._log('ERROR', "Missing needed parameters for instantiation: %s", str(missing))
            del self
            return

        if lvl:
            self._lvl: MaimaiDX.ChartLevel = lvl
        else:
            d_source: Optional[MDXDataSource] = getattr(self.__class__,
                                                        'data_source',
                                                        getattr(self, 'data_source', None))
            if d_source:
                constant = d_source.get_constant(self._song, self._type, self._diff)
                lvl = self.lvl_from_constant(constant)
                self._lvl = lvl if lvl else 'N/A'

        self._sync: MaimaiDX.RecordSync= sync if sync else ''
        self._combo: MaimaiDX.RecordCombo = combo if combo else ''

    def lvl_from_constant(self, constant: float) -> Optional[str]:
        lvl = str(constant).split('.')
        if not lvl:
            return None
        if len(lvl) == 2:
            if int(lvl[1]) >= 6:
                lvl[1] = '+'
            else:
                lvl[1] = ''

        return ''.join(lvl)

    def from_dict(self, import_dict: dict) -> bool:

        def invalid_format(key_s: str) -> bool:
            self._log('ERROR', "Invalid format for key(s) [%s]: %s", key_s, import_dict)
            return False

        key = import_dict.get('key', None)
        if isinstance(key, list) and len(key) == 3:
            self._song = key[0]
            self._type = key[1]
            self._diff = key[2]
        else:
            return invalid_format('key')
        record = import_dict.get('record', None)
        if isinstance(record, list) and len(record) == 4:
            if isinstance(record[0], float):
                self._achv = str(record[0]) + '%'
            else:
                self._achv = record[0]
            self._combo = record[2]
            self._sync = record[3]
        else:
            return invalid_format('record')
        sourced = import_dict.get('sourced', False)
        meta = import_dict.get('meta', [0.0, 'N/A', "None"])
        d_source: Optional[MDXDataSource] = getattr(self.__class__,
                                                    'data_source',
                                                    getattr(self, 'data_source', None))

        if sourced and not d_source:
            if len(meta) != 3:
                return invalid_format('meta')
            if meta[0] != 0.0:
                self._lvl_i = meta[0]
            self.lvl = meta[1]
            rating = import_dict.get('rating', 0)
            if rating > 0:
                self._rating = rating
        elif d_source:
            self._lvl_i = lvl = d_source.get_constant(self._song,self._type,self._diff)
            lvl = str(lvl).split('.')
            if not lvl:
                return invalid_format('song, type, diff')
            if len(lvl) == 2:
                if int(lvl[1]) >= 6:
                    lvl[1] = '+'
                else:
                    lvl[1] = ''
            self._lvl = ''.join(lvl)
        return True

    def from_str(self, import_str: str) -> bool:
        #logging helper
        import_dict = {}

        try:
            import_dict = json_load(import_str)
            if isinstance(import_dict, list):
                self._log('ERROR', "Tried importing multiple records, try RecordContainer.from_str() instead!")
                return False
        except Exception as e:
            self._log('ERROR', 'Invalid import string format (%s) exception: %s', import_str, str(e))
            return False

        if import_dict:
            return self.from_dict(import_dict)

        self._log('ERROR', 'Invalid import string format: %s', import_str)
        return False





    def lvl_from_constant(self, constant: float) -> Optional[str]:
        lvl = str(constant).split('.')
        if not lvl:
            return None
        if len(lvl) == 2:
            if int(lvl[1]) >= 6:
                lvl[1] = '+'
            else:
                lvl[1] = ''

        return ''.join(lvl)

    def from_dict(self, import_dict: dict) -> bool:

        def invalid_format(key_s: str) -> bool:
            self._log('ERROR', "Invalid format for key(s) [%s]: %s", key_s, import_dict)
            return False

        key = import_dict.get('key', None)
        if isinstance(key, list) and len(key) == 3:
            self._song = key[0]
            self._type = key[1]
            self._diff = key[2]
        else:
            return invalid_format('key')
        record = import_dict.get('record', None)
        if isinstance(record, list) and len(record) == 4:
            if isinstance(record[0], float):
                self._achv = str(record[0]) + '%'
            else:
                self._achv = record[0]
            self._combo = record[2]
            self._sync = record[3]
        else:
            return invalid_format('record')
        sourced = import_dict.get('sourced', False)
        meta = import_dict.get('meta', [0.0, 'N/A', "None"])
        d_source: Optional[MDXDataSource] = getattr(self.__class__,
                                                    'data_source',
                                                    getattr(self, 'data_source', None))

        if sourced and not d_source:
            if len(meta) != 3:
                return invalid_format('meta')
            if meta[0] != 0.0:
                self._lvl_i = meta[0]
            self.lvl = meta[1]
            rating = import_dict.get('rating', 0)
            if rating > 0:
                self._rating = rating
        elif d_source:
            self._lvl_i = lvl = d_source.get_constant(self._song,self._type,self._diff)
            lvl = str(lvl).split('.')
            if not lvl:
                return invalid_format('song, type, diff')
            if len(lvl) == 2:
                if int(lvl[1]) >= 6:
                    lvl[1] = '+'
                else:
                    lvl[1] = ''
            self._lvl = ''.join(lvl)
        return True

    def from_str(self, import_str: str) -> bool:
        #logging helper
        import_dict = {}

        try:
            import_dict = json_load(import_str)
            if isinstance(import_dict, list):
                self._log('ERROR', "Tried importing multiple records, try RecordContainer.from_str() instead!")
                return False
        except Exception as e:
            self._log('ERROR', 'Invalid import string format (%s) exception: %s', import_str, str(e))
            return False

        if import_dict:
            return self.from_dict(import_dict)

        self._log('ERROR', 'Invalid import string format: %s', import_str)
        return False





    def resolve_inputs(self):
        if not self._type or not self._diff or not self._song:
            raise ValueError("Missing key parameters for record!")


    @property
    def achievement(self):
        """Achievement String"""
        return self._achv

    @property
    def achievement_float(self) -> MaimaiDX.RecordAchievementFloat:
        """Achievement Float"""
        res: float = 0.0
        try:
            res = float(self._achv[:-1])
        except (ValueError, TypeError): pass
        return res

    @property
    def song(self) -> MaimaiDX.SongName:
        """Song Name"""
        return self._song

    @property
    def chart_type(self) -> MaimaiDX.ChartType:
        """Chart Type (DX/STD)"""
        return self._type

    @property
    def difficulty(self) -> MaimaiDX.ChartDifficulty:
        """Difficulty"""
        return self._diff

    @property
    def combo(self) -> MaimaiDX.RecordCombo:
        """Combo Label e.g. fc,fcp,fdx"""
        return self._combo

    @property
    def sync(self) -> MaimaiDX.RecordSync:
        """Sync label e.g. fs,fsp"""
        return self._sync

    @property
    def internal_level(self) -> MaimaiDX.ChartInternal:
        """
        Internal constant of chart.

        Fetches from source if set, or lower-bound guess from level label.
        """
        song_name = self._song.strip()
        if RecordEntry.data_source:
            res = RecordEntry.data_source.get_constant(song_name=song_name,chart_type=self._type,difficulty=self._diff)
        else:
            res = getattr(self, '_lvl_i', 0.0)
        if isinstance(res, float):
            if res > 0.0:
                self._fetched = True
                return res
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
    def rating(self) -> MaimaiDX.RecordRating:
        """
        Rating calculated from constants and self.internal_level property method.
        """
        rating = 0
        for score,constant,rank in MaimaiDX.SCORE_COEFFICIENT_TABLE:
            if self.achievement_float >= score:
                achv = 0.0
                if self.achievement_float <= 100.5:
                    achv = self.achievement_float
                else:
                    achv = 100.5
                curr = achv * _cached_calculation(constant, self.internal_level)
                if curr > rating:
                    rating = curr
        return floor(rating)

    @property
    def rank(self) -> MaimaiDX.RecordRank:
        result_rank: MaimaiDX.RecordRank = 'd'
        for score,_,rank in MaimaiDX.SCORE_COEFFICIENT_TABLE:
            if self.achievement_float >= score:
                result_rank = rank
        return result_rank

    def is_new(self) -> bool:
        if not getattr(self.__class__, 'data_source', getattr(self, 'data_source', None)):
            return False

        version = RecordEntry.data_source.get_song_version(song_name=self._song)
        return _is_current(version)

    @property
    def valid(self) -> bool:
        sheet = None
        if RecordEntry.data_source:
            sheet = RecordEntry.data_source.get_sheet(self.song,
                                                      self.chart_type,
                                                      self.difficulty)
        return sheet is not None

    def as_print_str(self) -> str:
        s_new = "NEW" if self.is_new() else "OLD"
        return "%s %s (%d) - %s: Rating=%d, Achievement=%d, Combo=%s, Sync=%s" % (s_new,
                                                                                  self.difficulty,
                                                                                  self.internal_level,
                                                                                  self.song,
                                                                                  self.rating,
                                                                                  self.achievement_float,
                                                                                  self.combo,
                                                                                  self.sync)


    def as_dict(self):
        """
        Convert the record object to a dictionary representation.

        Returns:
            dict: A dictionary containing the following keys:
                - key (list): A list containing [song, chart_type, difficulty]
                - meta (list): A list containing [internal_level, data_source_name or None]
                - sourced (bool): Indicates whether the record has valid data
                - record (list): A list containing [achievement_float (rounded to 4 decimals), rank, combo, sync]
                - rating: The calculated rating value for this record
        """
        return {"key": [self.song,
                self.chart_type,
                self.difficulty],

                "meta": [self.internal_level,
                         self._lvl,
                         self.data_source.__name__ if self._fetched else None],

                "sourced": self.valid,

                "record": [self.achievement,
                           self.rank,
                           self.combo,
                           self.sync],

                "rating": self.rating
                }
    #String Helpers
    def __repr__(self) -> str:
        return json_dump(self.as_dict(), ensure_ascii=False)


class RecordCollection(Logged):
    """Handle record entry at one time point."""
    entries: list[RecordEntry] = []

    def __init__(self,
                 entries: Optional[list[RecordEntry]] = None,
                 import_str: Optional[str] = None):

        if not entries:
            entries = []

        self.entries = entries
        self.unique = set([(e.song, e.chart_type, e.difficulty, e.achievement) for e in self.entries])
        self.record_map: dict = {(e.song, e.chart_type, e.difficulty): e for e in self.entries}

        if import_str: self.from_str(import_str)


    def __str__(self) -> str:
        return json_dump([entry.as_dict() for entry in self.entries], ensure_ascii=False)

    def _tuple_set(self, record: RecordEntry):
        return (record.song, record.chart_type, record.difficulty, record.achievement)

    def _tuple_map(self, record: RecordEntry):
        return (record.song, record.chart_type, record.difficulty)

    def remove(self, set_tuple: tuple[Any, Any, Any, Any],
                    replace: Optional[RecordEntry] = None):
        for i,r in enumerate(self.entries):
            if (r.song, r.chart_type, r.difficulty, r.achievement) == set_tuple:
                self.entries.pop(i)
                if replace:
                    self.entries.insert(i, replace)
                break

    def add(self, record: RecordEntry):
        if self._tuple_set(record) in self.unique: return

        if self._tuple_map(record) in self.record_map:
            current = self.record_map[self._tuple_map(record)]
            if record.achievement_float > current.achievement_float:
                #upscore
                self.unique.remove(self._tuple_set(current))

                self.remove(self._tuple_set(current), replace=record)
                self.record_map[self._tuple_map(record)] = record

                self.unique.add(self._tuple_set(record))
            return

        self.record_map[self._tuple_map(record)] = record
        self.unique.add((record.song, record.chart_type, record.difficulty, record.achievement))
        self.entries.append(record)

    def compare(self, older: 'RecordCollection'):
        newscores, upscores, downscores = (0, 0, 0)
        result: list[tuple[RecordEntry, ScoreDifference]] = []

        difference = self.unique - older.unique
        for diff in difference:
            d_song, d_type, d_diff, _ = (d_tuple) = diff
            d_query = (d_song, d_type, d_diff)

            #if not in ours, current container is most likely a subset of all records
            #thus there's going to be alot of"oh deleted score!"
            #but if they did delete the sheet, need a datasource logic to verify.
            if d_tuple in self.unique:
                if d_query not in self.record_map:
                    raise ValueError("Unique set and record map mismatch!")

                this_record: RecordEntry = self.record_map[d_query]

                #if score did not exist -> newscore
                if (d_query) not in older.record_map:
                    newscores += 1
                    result.append((this_record, this_record.achievement_float))
                else:
                    other_record = older.record_map[d_query]

                    #if this is higher than older -> upscore
                    achv_diff = this_record.achievement_float - other_record.achievement_float

                    if achv_diff > 0:
                        upscores += 1
                    elif achv_diff < 0:
                        #normally not possible unless comparing with recent playlogs
                        downscores += 1

                    result.append((this_record, achv_diff))

        return (upscores, downscores, newscores), result

    def from_list(self, import_list: list[dict]):
        for record_dict in import_list:
            record = RecordEntry(import_dict=record_dict)
            if record:
                self.add(record)
            else:
                self._log('ERROR', "Error importing entry: %s", str(record))

    def from_str(self, import_str: str):
        try:
            import_lst = json_load(import_str)
            if not import_lst: raise ValueError(f"Failed to load JSON from string: {import_str}")
            self.from_list(import_lst)
        except Exception as e:
            self._log('ERROR', 'Invalid import string format (%s) exception: %s', import_str, str(e))

    def get_top_50(self):
        new: list[RecordEntry] = []
        old: list[RecordEntry] = []
        for e in self.entries:
            if e.is_new():
                new.append(e)
            else:
                old.append(e)

        new = sorted(new, key=lambda x: (-x.rating, -x.achievement_float, -x.internal_level))
        old = sorted(old, key=lambda x: (-x.rating, -x.achievement_float, -x.internal_level))

        if len(new) > 15:
            new = new[:15]
        if len(old) > 35:
            old = old[:35]

        new_rating = sum(e.rating for e in new)
        old_rating = sum(e.rating for e in old)
        total = new_rating + old_rating

        return (new, new_rating), (old, old_rating), total

















