"""External datasource connectors for internal constants, etc."""
from functools import lru_cache
from collections.abc import Callable
import logging
from types import MethodType
from typing import Optional, Any, Union
from abc import ABC, abstractmethod
import requests

from app.core.games.maimaidx import MaimaiDX


ConstantMapReturnValue = Union[MaimaiDX.ChartInternalMap, MaimaiDX.ChartInternal, None]
VERSION_LIST = MaimaiDX.VERSION_LIST


class MDXDataSource(ABC):
    """
    Base class for datasources outlining methods
    """
    _data: Union[dict,None]
    _data_constant: MaimaiDX.ChartInternalMap
    _data_song: dict[MaimaiDX.SongName,dict]
    _data_sheet: MaimaiDX.ChartSheetMap
    ready: bool

    @classmethod
    @abstractmethod
    def merge_same_sources(cls, *sources) -> list[bool] | bool:
        """
        Merge multiple datasources with the same HTML value format.

        Args:
            *sources: Variable number of data sources (type varies by subclass)

        Returns:
            - list[bool]: if merging multiple sources into this class
            - bool: if only merging one source
        """
        pass


    @classmethod
    @abstractmethod
    def __init__(cls) -> None:
        """
        Initialise internal values here
        """
        cls.missing_sheets = []
        cls._data: Union[dict,None] = None
        cls._data_constant: MaimaiDX.ChartInternalMap = {}
        cls._data_song: dict[MaimaiDX.SongName,dict] = {}
        cls._data_sheet: MaimaiDX.ChartSheetMap = {}
        cls.ready = False


    @classmethod
    @abstractmethod
    def get_sheet(cls, song_name: Optional[MaimaiDX.SongName] = None, chart_type: Optional[MaimaiDX.ChartType] = None, difficulty: Optional[MaimaiDX.ChartDifficulty] = None) -> Optional[dict]:
        """
        Args: Optional[QueryParameters]
        Returns: dict or None
        """
        pass

    @classmethod
    @abstractmethod
    def get_song(cls, song_name: Optional[MaimaiDX.SongName] = None) -> Optional[dict[MaimaiDX.SongName, dict[str, Any]]]:
        """
        Args:
            song_name (Optional[MDXSongName]): The name of the song to retrieve

        Returns:
            Optional[dict[MDXSongName, dict[str, Any]]]:
                - If song_name is None: Returns full song data map
                - If song_name is provided: Returns song data dict or None
        """
        pass

    @classmethod
    @abstractmethod
    def get_constant(cls, song_name: Optional[MaimaiDX.SongName] = None, chart_type: Optional[MaimaiDX.ChartType] = None, difficulty: Optional[MaimaiDX.ChartDifficulty] = None) -> float:
        """
        Args: Optional[QueryParameters]
        Returns: float or None
        """
        pass

    @classmethod
    @abstractmethod
    def get_song_version(cls, version_code: Optional[Union[str,int]] = None, song_name: Optional[MaimaiDX.SongName] = None) -> Optional[str]:
        pass

    @classmethod
    def get_stats(cls) -> tuple[int,int]:
        return len(cls._data_song), len(cls._data_sheet)

class DataSourceDummy(MDXDataSource):
    @classmethod
    def __init__(cls, name: str):
        cls.__name__ = name
class CachedUtils:
    @classmethod
    def _clear_cached_method(cls, method: Any) -> None:
        target = getattr(method, "__func__", method)
        cache_clear = getattr(target, "cache_clear", None)
        if callable(cache_clear):
            cache_clear()

