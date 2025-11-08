"""Typing definitions for MaimaiDX"""

from typing import Literal, Union

MDXGameCoefficient = float

MDXSongName = str
MDXChartLevel = str
MDXChartInternal = float
MDXChartType = Literal['STD','DX']
MDXChartDifficulty = Literal['ReMASTER', 'MASTER', 'EXPERT', 'ADVANCED','BASIC']

MDXChartValue = Union[MDXSongName,MDXChartType,MDXChartDifficulty]
MDXChartParams = Literal['chart_type', 'song_name', 'difficulty']
MDXChartTuple = tuple[MDXSongName,MDXChartType,MDXChartDifficulty]
MDXChartQueryArgs = dict[MDXChartParams,Union[MDXSongName,MDXChartDifficulty,MDXChartType]]
MDXChartInternalMap = dict[MDXChartTuple,MDXChartInternal]
MDXChartSheetMap =dict[MDXChartTuple,dict]

MDXRecordParams = Literal['achievement','achievement_float','rank']
MDXRecordRank = Literal['sssp','sss','ssp','ss','sp','s','aaa','aa','a','bbb','bb','b','c','d']
MDXRecordSync = Literal['','sync','fs','fsp','fdx','fdxp']
MDXRecordCombo = Literal['','fc','fcp','ap','app']
MDXRecordAchievement = str
MDXRecordAchievementFloat = float
MDXRecordRating = int

MDXRecordValue = Union[MDXRecordRank,
                       MDXRecordAchievement,
                       MDXRecordAchievementFloat,
                       MDXRecordRating]


MDXDataValue = Union[MDXRecordValue,MDXChartValue]
