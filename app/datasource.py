import requests
import logging
from typing import Optional, Final
from app.data_types.maimaidx import *
from abc import ABC, abstractmethod

ConstantMapReturnValue = Union[MDXChartInternalMap, MDXChartInternal, None]

class MDXDataSource(ABC):
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
    def get_constant(cls, song_name: Optional[MDXSongName] = None, chart_type: Optional[MDXChartType] = None, difficulty: Optional[MDXChartDifficulty] = None) -> ConstantMapReturnValue:
        pass
    
class OtogeDB(MDXDataSource):
    difficulties: Final[dict[str,MDXChartDifficulty]] = {'remas':'ReMASTER','mas':'MASTER','exp':'EXPERT','adv':'ADVANCED','bas':'BASIC'} 
    types: Final[dict[str,MDXChartType]] = {'dx_':'DX','':'STD'}
    
    @classmethod
    def __init__(cls,url='https://otoge-db.net/maimai/data/music-ex-intl.json'):
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
        if not cls._data: return {}
        for e in cls._data:
            song: MDXSongName = e["title"]
            cls._songs.add(song)
            cls._init_song(e,song)
            cls._init_sheet(e,song)
            
            #CHART CONSTANTS TODO: clean this up
            if 'dx_lev_mas' in e:
                if "dx_lev_remas_i" in e and e["dx_lev_remas_i"] != '':
                    cls._data_constant[(song,'DX','ReMASTER')] = float(e["dx_lev_remas_i"])
                if "dx_lev_mas_i" in e and e["dx_lev_mas_i"] != "": 
                    cls._data_constant[(song,'DX','MASTER')] = float(e["dx_lev_mas_i"])
                if "dx_lev_exp_i" in e and e["dx_lev_exp_i"] != "": 
                    cls._data_constant[(song,'DX','EXPERT')]= float(e["dx_lev_exp_i"])
                if "dx_lev_adv_i" in e and e["dx_lev_adv_i"] != "": 
                    cls._data_constant[(song,'DX','ADVANCED')] = float(e["dx_lev_adv_i"])
                if "dx_lev_bas_i" in e and e["dx_lev_bas_i"] != "": 
                    cls._data_constant[(song,'DX','BASIC')] = float(e["dx_lev_bas_i"])
        
            if 'lev_mas' in e:
                if "lev_remas_i" in e and e["lev_remas_i"] != '':
                    cls._data_constant[(song,'STD','ReMASTER')] = float(e["lev_remas_i"])
                if "lev_mas_i" in e and e["lev_mas_i"] != "": 
                    cls._data_constant[(song,'STD','MASTER')] = float(e["lev_mas_i"])
                if "lev_exp_i" in e and e["lev_exp_i"] != "": 
                    cls._data_constant[(song,'STD','EXPERT')] = float(e["lev_exp_i"])
                if "lev_adv_i" in e and e["lev_adv_i"] != "": 
                    cls._data_constant[(song,'STD','ADVANCED')] = float(e["lev_adv_i"])
                if "lev_bas_i" in e and e["lev_bas_i"] != "": 
                    cls._data_constant[(song,'STD','BASIC')] = float(e["lev_bas_i"])
    
    @classmethod
    def _init_song(cls, e:dict, s: MDXSongName):
        SongDataMap: Final[dict] = {'artist':'artist','catcode':'category','bpm':'bpm','image_url':'image_url','wiki_url':'wiki_url','title_kana':'kana'}
        for field, key in SongDataMap.items():
            if s not in cls._data_song: 
                cls._data_song[s] = {}
                
            if field in e: 
                cls._data_song[s][key] = e[field]
            
    @classmethod
    def _init_sheet(cls, e: dict, s: MDXSongName):
        for t_syntax, t in cls.types.items():
            for d_syntax, d in cls.difficulties.items():
                if (s,t,d) not in cls._data_sheet: cls._data_sheet[(s,t,d)] = {}
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
            
    @classmethod
    def get_sheet(cls, song_name: Optional[MDXSongName] = None, chart_type: Optional[MDXChartType] = None, difficulty: Optional[MDXChartDifficulty] = None) -> Optional[dict]:
        if song_name is None and chart_type is None and difficulty is None:
            return cls._data_sheet
        elif song_name is not None and chart_type is not None and difficulty is not None:
            query_tuple: MDXChartTuple = (song_name, chart_type, difficulty)
            if query_tuple in cls._data_constant:
                return cls._data_sheet[query_tuple]
            else:
                cls.logger.debug(f"Queried ({song_name},{chart_type},{difficulty}) with no results.")
                return None
            
    @classmethod
    def get_song(cls, song_name: Optional[MDXSongName] = None) -> Optional[dict]:
        if song_name is None:
            return cls._data_song
        else:
            if song_name in cls._data_constant:
                return cls._data_song[song_name]
            else:
                return None
            
    @classmethod
    def get_constant(cls, song_name: Optional[MDXSongName] = None, chart_type: Optional[MDXChartType] = None, difficulty: Optional[MDXChartDifficulty] = None) -> ConstantMapReturnValue:
        if song_name is None and chart_type is None and difficulty is None:
            return cls._data_constant
        elif song_name is not None and chart_type is not None and difficulty is not None:
            query_tuple: MDXChartTuple = (song_name, chart_type, difficulty)
            if query_tuple in cls._data_constant:
                return cls._data_constant[query_tuple]
            else:
                return 0.0

            
            
            
            