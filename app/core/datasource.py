"""External datasource connectors for internal constants, etc."""
import logging
from typing import Optional, Final, Any
from abc import ABC, abstractmethod
import requests

# pylint: disable=unused-wildcard-import
from app.types.maimaidx import *


ConstantMapReturnValue = Union[MDXChartInternalMap, MDXChartInternal, None]

class MDXDataSource(ABC):
    """
    Base class for datasources outlining methods
    """
    _data: Union[dict,None]
    _data_constant: MDXChartInternalMap
    _data_song: dict[MDXSongName,dict]
    _data_sheet: MDXChartSheetMap
    ready: bool

    @classmethod
    @abstractmethod
    def __init__(cls) -> None:
        """
        Initialise internal values here
        """
        cls._data: Union[dict,None] = None
        cls._data_constant: MDXChartInternalMap = {}
        cls._data_song: dict[MDXSongName,dict] = {}
        cls._data_sheet: MDXChartSheetMap = {}
        cls.ready = False

    @classmethod
    @abstractmethod
    def get_sheet(cls, song_name: Optional[MDXSongName] = None, chart_type: Optional[MDXChartType] = None, difficulty: Optional[MDXChartDifficulty] = None) -> Optional[dict]:
        """
        Args: Optional[QueryParameters]
        Returns: dict or None
        """
        pass

    @classmethod
    @abstractmethod
    def get_song(cls, song_name: Optional[MDXSongName] = None) -> Optional[dict]:
        """
        Args: Optional[QueryParameters]
        Returns: dict or None
        """
        pass

    @classmethod
    @abstractmethod
    def get_constant(cls, song_name: Optional[MDXSongName] = None, chart_type: Optional[MDXChartType] = None, difficulty: Optional[MDXChartDifficulty] = None) -> ConstantMapReturnValue:
        """
        Args: Optional[QueryParameters]
        Returns: float or None
        """
        pass

class OtogeDB(MDXDataSource):
    """
    OtogeDB external datasource.
    """

    DIFFICULTY_MAP: Final[dict[str,MDXChartDifficulty]] = {'remas':'ReMASTER','mas':'MASTER','exp':'EXPERT','adv':'ADVANCED','bas':'BASIC'}
    TYPE_MAP: Final[dict[str,MDXChartType]] = {'dx_':'DX','':'STD'}

    @classmethod
    def __init__(cls,url='https://otoge-db.net/maimai/data/music-ex-intl.json'):
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
            cls.logger.info(f"Fetched {len(cls._songs)} songs and {len(cls._data_sheet)} sheets from {url}")
            cls.ready = True
        except requests.exceptions.RequestException as e:
            cls.logger.exception(f"Failed to fetch data from {url}: {e}")
            cls._data = None

    @classmethod
    def _init_data(cls):
        """
        Initialises data and calls other init functions.
        """
        if cls._data:
            for e in cls._data:
                song: MDXSongName = e["title"]
                cls._songs.add(song)
                cls._init_song(e,song)



    @classmethod
    def _init_song(cls, e:dict, s: MDXSongName):
        """
        Initialise song metadata map.
        """
        song_data_map: Final[dict] = {'artist':'artist','catcode':'category','bpm':'bpm','image_url':'image_url','wiki_url':'wiki_url','title_kana':'kana'}
        for field, key in song_data_map.items():
            if s not in cls._data_song:
                charts = cls._init_sheet(e,s)
                cls._data_song[s] = {'charts': charts}

            if field in e:
                cls._data_song[s][key] = e[field]




    @classmethod
    def _init_sheet(cls, e: dict, s: MDXSongName):
        """
        Initialise internal sheet maps.
        """
        return_value: dict[
                            MDXChartType,
                            dict[
                                MDXChartDifficulty,
                                Optional[dict[Literal['internal', 'designer', 'notes'],
                                              Optional[Union[dict,str]]]]
                            ]
                        ] = {'DX':{},'STD':{}}

        for t_syntax, t in cls.TYPE_MAP.items():
            for d_syntax, d in cls.DIFFICULTY_MAP.items():
                if (s,t,d) not in cls._data_sheet:
                    cls._data_sheet[(s,t,d)] = {}

                if f'{t_syntax}lev_{d_syntax}_i' in e:
                    internal_constant = e[f'{t_syntax}lev_{d_syntax}_i']

                    try:
                        internal_constant = float(internal_constant)
                        cls._data_sheet[(s,t,d)]['internal'] = str(round(internal_constant,1))
                    except (ValueError):
                        cls._data_sheet[(s,t,d)]['internal'] = internal_constant
                        internal_constant = 0.0

                    cls._data_constant[(s,t,d)] = internal_constant


                if f'{t_syntax}lev_{d_syntax}_designer' in e:
                    cls._data_sheet[(s,t,d)]['designer'] = e[f'{t_syntax}lev_{d_syntax}_designer']

                if f'{t_syntax}lev_{d_syntax}_notes' in e:
                    if 'notes' not in cls._data_sheet[(s,t,d)]: cls._data_sheet[(s,t,d)]['notes'] = {}
                    cls._data_sheet[(s,t,d)]['notes']['total'] = e[f'{t_syntax}lev_{d_syntax}_notes']

                if f'{t_syntax}lev_{d_syntax}_notes_tap' in e:
                    cls._data_sheet[(s,t,d)]['notes']['tap'] = e[f'{t_syntax}lev_{d_syntax}_notes_tap']

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
    def get_sheet(cls, song_name: Optional[MDXSongName] = None, chart_type: Optional[MDXChartType] = None, difficulty: Optional[MDXChartDifficulty] = None) -> Optional[dict]:
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
        if song_name is not None and chart_type is not None and difficulty is not None:
            query_tuple: MDXChartTuple = (song_name, chart_type, difficulty)
            if query_tuple in cls._data_constant:
                return cls._data_sheet[query_tuple]
            cls.logger.debug(f"Queried ({song_name},{chart_type},{difficulty}) with no results.")
            return None

        return cls._data_sheet

    @classmethod
    def get_song(cls, song_name: Optional[MDXSongName] = None) -> Optional[dict]:
        """
        Retrieves a sheet with sheet data (designer,notes).
        Args:
            song_name (MDXSongName)

        Returns:
            song_data (dict): defaults to None
            song_data_map (dict): dict[song_name,song_data]
        """
        if song_name is None:
            return cls._data_song
        else:
            if song_name in cls._data_constant:
                return cls._data_song[song_name]
            return None

    @classmethod
    def get_constant(cls, song_name: Optional[MDXSongName] = None, chart_type: Optional[MDXChartType] = None, difficulty: Optional[MDXChartDifficulty] = None) -> ConstantMapReturnValue:
        """
        Retrieves a sheet with sheet data (designer,notes).
        Args:
            song_name (MDXSongName)
            chart_type (MDXChartType)
            difficulty (MDXChartDifficulty)
        Returns:
            constant (float): 0.0 if not found
        """
        if song_name is None and chart_type is None and difficulty is None:
            return cls._data_constant
        elif song_name is not None and chart_type is not None and difficulty is not None:
            query_tuple: MDXChartTuple = (song_name, chart_type, difficulty)
            if query_tuple in cls._data_constant:
                return cls._data_constant[query_tuple]
            else:
                return 0.0




