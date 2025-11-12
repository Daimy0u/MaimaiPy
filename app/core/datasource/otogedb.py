"""OtogeDB Datasources"""

import logging
import requests

from functools import lru_cache
from typing import Final, Optional, Iterable, Literal, Union

from .base import MDXDataSource, CachedUtils, VERSION_LIST
from app.core.games.maimaidx import MaimaiDX

class OtogeDB(MDXDataSource, CachedUtils):
    """
    OtogeDB external datasource.
    """
    __name__ = 'OtogeDB'
    DIFFICULTY_MAP: Final[dict[str,MaimaiDX.ChartDifficulty]] = {'remas':'ReMASTER','mas':'MASTER','exp':'EXPERT','adv':'ADVANCED','bas':'BASIC'}
    TYPE_MAP: Final[dict[str,MaimaiDX.ChartType]] = {'dx_':'DX','':'STD'}

    @classmethod
    def merge_same_sources(cls, *sources: type['OtogeDB']) -> list[bool] | bool:
        if not cls._data:
            raise ValueError("Called merge before class data was initialised!")
        flag = [False for s in sources]
        for idx,s in enumerate(sources):
            if isinstance(s, dict):
                cls._data.update(s)
                cls._init_data(s)
                flag[idx] = True
        if len(flag) == 1: return flag[0]
        else: return flag


    @classmethod
    def __init__(cls, url='https://otoge-db.net/maimai/data/music-ex-intl.json',
                 useFull: bool = False,
                 url_full='https://otoge-db.net/maimai/data/music-ex.json'):
        """
        Initialises class attributes and calls main data init function.
        """
        super().__init__()
        cls.logger = logging.getLogger(cls.__name__)
        try:
            resp = requests.get(url)
            resp.raise_for_status()
            cls._versions = set()
            cls._songs = set()
            cls._data = resp.json()
            cls._init_data()

            if useFull:
                resp_f = requests.get(url_full)
                resp_f.raise_for_status()
                resp_f_json = resp_f.json()
                cls._data = cls._data + resp_f.json()

                resp_f_json = [e for e in resp_f_json
                               if 'version' in e
                               and e['version'][:3] != "260"]

                cls._init_data(resp_f_json)

            cls.logger.info(f"Fetched {len(cls._songs)} songs and {len(cls._data_sheet)} sheets from {url}")
            cls.ready = True

        except requests.exceptions.RequestException as e:
            cls.logger.exception(f"Failed to fetch data from {url}: {e}")
            cls._data = None

    @classmethod
    def _init_data(cls, data: Optional[Iterable] = None):
        """
        Initialises data and calls other init functions.
        """
        if not data:
            if cls._data:
                data = cls._data
            if not cls._data:
                raise ValueError("Initialisation failed, missing internal data.")
        if data:
            for e in data:
                cls._init_entry(e)

    @classmethod
    def _init_entry(cls, e: dict):
        """
        Initialises a data entry.
        """
        song: MaimaiDX.SongName = e["title"]
        version = e["version"] = cls.get_song_version(e["version"])
        cls._versions.add(version)
        cls._songs.add(song)
        cls._init_song(e,song)

    @classmethod
    def _init_song(cls, e:dict, s: MaimaiDX.SongName):
        """
        Initialise song metadata map and calls sheet init functions.
        """
        song_data_map: Final[dict] = {'version':'version','artist':'artist','catcode':'category','bpm':'bpm','image_url':'image_url','wiki_url':'wiki_url','title_kana':'kana'}
        for field, key in song_data_map.items():
            if s not in cls._data_song:
                charts = cls._init_sheet(e,s)
                cls._data_song[s] = {'charts': charts}

            if field in e:
                cls._data_song[s][key] = e[field]




    @classmethod
    def _init_sheet(cls, e: dict, s: MaimaiDX.SongName):
        """
        Initialise internal sheet maps.
        """
        return_value: dict[
                            MaimaiDX.ChartType,
                            dict[
                                MaimaiDX.ChartDifficulty,
                                Optional[dict[Literal['internal', 'designer', 'notes'],
                                              Optional[Union[dict,str]]]]
                            ]
                        ] = {'DX':{},'STD':{}}

        for t_syntax, t in cls.TYPE_MAP.items():
            for d_syntax, d in cls.DIFFICULTY_MAP.items():
                if (s,t,d) not in cls._data_sheet:
                    cls._data_sheet[(s,t,d)] = {}

                #defaults
                cls._data_sheet[(s,t,d)]['level'] = 'N/A'
                cls._data_sheet[(s,t,d)]['internal'] = str(0.0)
                cls._data_sheet[(s,t,d)]['designer'] = 'N/A'
                cls._data_sheet[(s,t,d)]['notes'] = {'total':'N/A','tap':'N/A','touch':'N/A','hold':'N/A','slide':'N/A','break':'N/A'}


                if f'{t_syntax}lev_{d_syntax}_i' in e:
                    internal_constant = e[f'{t_syntax}lev_{d_syntax}_i']

                    try:
                        internal_constant = float(internal_constant)
                        cls._data_sheet[(s,t,d)]['internal'] = str(round(internal_constant,1))
                    except (ValueError):
                        cls._data_sheet[(s,t,d)]['internal'] = internal_constant
                        internal_constant = 0.0

                    cls._data_constant[(s,t,d)] = internal_constant

                if f'{t_syntax}lev_{d_syntax}' in e:
                    cls._data_sheet[(s,t,d)]['level'] = e[f'{t_syntax}lev_{d_syntax}']

                if f'{t_syntax}lev_{d_syntax}_designer' in e:
                    cls._data_sheet[(s,t,d)]['designer'] = e[f'{t_syntax}lev_{d_syntax}_designer']

                if f'{t_syntax}lev_{d_syntax}_notes' in e:
                    cls._data_sheet[(s,t,d)]['notes']['total'] = e[f'{t_syntax}lev_{d_syntax}_notes']

                if f'{t_syntax}lev_{d_syntax}_notes_tap' in e:
                    cls._data_sheet[(s,t,d)]['notes']['tap'] = e[f'{t_syntax}lev_{d_syntax}_notes_tap']

                if f'{t_syntax}lev_{d_syntax}_notes_touch' in e:
                    cls._data_sheet[(s,t,d)]['notes']['touch'] = e[f'{t_syntax}lev_{d_syntax}_notes_touch']

                if f'{t_syntax}lev_{d_syntax}_notes_hold' in e:
                    cls._data_sheet[(s,t,d)]['notes']['hold'] = e[f'{t_syntax}lev_{d_syntax}_notes_hold']

                if f'{t_syntax}lev_{d_syntax}_notes_slide' in e:
                    cls._data_sheet[(s,t,d)]['notes']['slide'] = e[f'{t_syntax}lev_{d_syntax}_notes_slide']

                if f'{t_syntax}lev_{d_syntax}_notes_break' in e:
                    cls._data_sheet[(s,t,d)]['notes']['break'] = e[f'{t_syntax}lev_{d_syntax}_notes_break']

                return_value[t][d] = cls._data_sheet.get((s,t,d))

        if not return_value['DX']:
            del return_value['DX']
        elif not return_value['STD']:
            del return_value['STD']

        return return_value

    @classmethod
    @lru_cache
    def _cached_sheet(cls, song_name, chart_type, difficulty):
        if song_name is not None and chart_type is not None and difficulty is not None:
            query_tuple: MaimaiDX.ChartTuple = (song_name, chart_type, difficulty)
            if query_tuple in cls._data_constant:
                return cls._data_sheet[query_tuple]
            else:
                cls.missing_sheets.append(query_tuple)
                cls.logger.debug(f"Queried ({song_name},{chart_type},{difficulty}) with no results.")
                return None

        return cls._data_sheet

    @classmethod
    def get_sheet(cls, song_name: Optional[MaimaiDX.SongName] = None, chart_type: Optional[MaimaiDX.ChartType] = None, difficulty: Optional[MaimaiDX.ChartDifficulty] = None) -> Optional[dict]:
        """
        Retrieves a sheet with sheet data (designer,notes).
        Args:
            song_name (MDXSongName)
            chart_type (MDXChartType)
            difficulty (MDXChartDifficulty)

        Returns:
            sheet (dict): defaults to None
            sheet_map (dict): dict[args,sheet]
        """
        return cls._cached_sheet(song_name,chart_type,difficulty)

    @classmethod
    @lru_cache
    def _cached_song(cls, song_name):
        if song_name is None:
            return cls._data_song
        else:
            if song_name in cls._songs:
                return cls._data_song[song_name]
            return None

    @classmethod
    def get_song(cls, song_name: Optional[MaimaiDX.SongName] = None) -> Optional[dict]:
        """
        Retrieves a sheet with sheet data (designer,notes).
        Args:
            song_name (MDXSongName)

        Returns:
            song_data (dict): defaults to None
            song_data_map (dict): dict[song_name,song_data]
        """
        return cls._cached_song(song_name)

    @classmethod
    @lru_cache
    def _cached_constant(cls, song_name, chart_type, difficulty) -> float:
        if song_name is not None and chart_type is not None and difficulty is not None:
            query_tuple: MaimaiDX.ChartTuple = (song_name, chart_type, difficulty)
            if query_tuple in cls._data_constant:
                return cls._data_constant[query_tuple]
        return 0.0

    @classmethod
    def get_constant(cls, song_name: Optional[MaimaiDX.SongName] = None, chart_type: Optional[MaimaiDX.ChartType] = None, difficulty: Optional[MaimaiDX.ChartDifficulty] = None) -> float:
        """
        Retrieves a sheet with sheet data (designer,notes).
        Args:
            song_name (MDXSongName)
            chart_type (MDXChartType)
            difficulty (MDXChartDifficulty)
        Returns:
            constant (float): 0.0 if not found
        """
        return cls._cached_constant(song_name, chart_type, difficulty)

    @classmethod
    @lru_cache
    def _get_version(cls, version_code = None, song_name = None) -> str:
        version = 'N/A'
        if version_code:
            if not isinstance(version_code, str):
                version_code = str(version_code)

            version_major = version_code[:3]

            if version_major in VERSION_LIST:
                version = VERSION_LIST[version_major]

        elif song_name:
            if song_name in cls._songs:
                song = cls.get_song(song_name)
                song = song if song else {}

                if 'version' in song:
                    version = song['version']

        return version


    @classmethod
    def get_song_version(cls, version_code: str | int | None = None, song_name: str | None = None):
        return cls._get_version(version_code=version_code, song_name=song_name)


    @property
    def versions(self):
        return list(self._versions)

class OtogeDBJPEX(OtogeDB):
    @classmethod
    def __init__(cls):
        super().__init__('https://otoge-db.net/maimai/data/music-ex.json')
        cls.__name__ = 'OtogeDB_JPEX'