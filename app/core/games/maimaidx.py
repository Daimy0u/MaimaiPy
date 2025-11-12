from enum import Enum
from typing import Final, Literal, Union, TypeAlias, ClassVar

class SiteMeta(Enum):
    id: ClassVar[str]
    Home: ClassVar[str]
    Back: ClassVar[str]
class PageRoutes(Enum):
    Home: str
    PlayerData: str
    RecordData: str
    Record: dict
    UserOptions: str
class GameMetadata:
    Site: ClassVar[type[SiteMeta]] = SiteMeta
    Routes: ClassVar[type[PageRoutes]] = PageRoutes
    pass
class MaimaiDX(GameMetadata):
    __name__ = 'maimaidx'

    ScoreCoefficient: TypeAlias = float
    SongName: TypeAlias = str | Literal['N/A']
    ChartLevel: TypeAlias = str | Literal['N/A']
    ChartInternal: TypeAlias = float | Literal[0]
    ChartType: TypeAlias = Literal['STD','DX']
    ChartDifficulty: TypeAlias = Literal['ReMASTER', 'MASTER', 'EXPERT', 'ADVANCED','BASIC']

    RecordAchievement: TypeAlias = str
    RecordAchievementFloat: TypeAlias = float
    RecordRating: TypeAlias = int
    RecordRank: TypeAlias = Literal['sssp','sss','ssp','ss','sp','s','aaa','aa','a','bbb','bb','b','c','d']
    RecordSync: TypeAlias = Literal['','sync','fs','fsp','fdx','fdxp']
    RecordCombo: TypeAlias = Literal['','fc','fcp','ap','app']

    class Site(SiteMeta):
        id = 'maimaidxex'
        Home = "https://maimaidx-eng.com/maimai-mobile"
        Back = "https://maimai.sega.com/"
    class Routes(PageRoutes):
        Home = '/home'
        PlayerData = '/playerData'
        RecordData = '/record'
        Record = {'ReMASTER':'/record/musicGenre/search/?genre=99&diff=4',
                'MASTER':'/record/musicGenre/search/?genre=99&diff=3',
                'EXPERT':'/record/musicGenre/search/?genre=99&diff=2',
                'ADVANCED': '/record/musicGenre/search/?genre=99&diff=1',
                'BASIC':'/record/musicGenre/search/?genre=99&diff=0'}
        UserOptions = '/home/userOption'

    VERSION_LIST: Final[dict] = {"100": "maimai",
                                 "110": "maimai PLUS",
                                 "120": "maimai GreeN",
                                 "130": "maimai GreeN PLUS",
                                 "140": "maimai ORANGE",
                                 "150": "maimai ORANGE PLUS",
                                 "160": "maimai PiNK",
                                 "170": "maimai PiNK PLUS",
                                 "180": "maimai MURASAKi",
                                 "185": "maimai MURASAKi PLUS",
                                 "190": "maimai MiLK",
                                 "195": "maimai MiLK PLUS",
                                 "199": "maimai FiNALE",
                                 "200": "maimai でらっくす",
                                 "205": "maimai でらっくす PLUS",
                                 "210": "maimai Splash",
                                 "215": "maimai Splash PLUS",
                                 "220": "maimai UNiVERSE",
                                 "225": "maimai UNiVERSE PLUS",
                                 "230": "maimai FESTiVAL",
                                 "235": "maimai FESTiVAL PLUS",
                                 "240": "maimai BUDDiES",
                                 "245": "maimai BUDDiES PLUS",
                                 "250": "maimai PRiSM",
                                 "255": "maimai PRiSM PLUS",
                                 "260": "maimai CiRCLE"}
    VERSION_EX = set(["255",
                      "PRISM PLUS",
                      "MAIMAI PRISM PLUS"])

    VERSION_JP = set(["260",
                      "CIRCLE",
                      "MAIMAI CIRCLE"])

    CHART_DIFFICULTIES: Final[list[ChartDifficulty]] = ['ReMASTER',
                                                           'MASTER',
                                                           'EXPERT',
                                                           'ADVANCED',
                                                           'BASIC']

    CHART_TYPES: Final[list[ChartType]] = ['DX','STD']

    SCORE_COEFFICIENT_TABLE: Final[list[tuple[RecordAchievementFloat,
                                              ScoreCoefficient,
                                              RecordRank]]] = [(0, 0, 'd'),
                                                                  (50, 8, 'c'),
                                                                  (60, 9.6, 'b'),
                                                                  (70, 11.2, 'bb'),
                                                                  (75, 12.0, 'bbb'),
                                                                  (80, 13.6, 'a'),
                                                                  (90, 15.2, 'aa'),
                                                                  (94, 16.8, 'aaa'),
                                                                  (97, 20, 's'),
                                                                  (98, 20.3, 'sp'),
                                                                  (99, 20.8, 'ss'),
                                                                  (99.5, 21.1, 'ssp'),
                                                                  (99.9999, 21.4, 'ssp'),
                                                                  (100, 21.6, 'sss'),
                                                                  (100.4999, 22.2, 'sss'),
                                                                  (100.5, 22.4, 'sssp')]


    ChartValue: TypeAlias = Union[SongName, ChartType, ChartDifficulty]
    ChartParams: TypeAlias = Literal['song_name', 'chart_type', 'difficulty']
    ChartTuple: TypeAlias = tuple[SongName, ChartType, ChartDifficulty]
    ChartKeywordArgs: TypeAlias = dict[ChartParams, str]

    # Return Value Maps
    ChartInternalMap: TypeAlias = dict[ChartTuple, ChartInternal]
    ChartSheetMap: TypeAlias = dict[ChartTuple, dict]
    SongMap: TypeAlias = dict[SongName, dict]
