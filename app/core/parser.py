"""Provides parser classes as session-class instance wrappers."""

from typing import Optional, Literal, Final, Union, get_args, cast
import asyncio
import bs4

from app.core.session import MaimaiEXSession
from app.models.record import RecordEntry
from app.core.games.maimaidx import MaimaiDX

RecordEntryKeys = Literal['type','song','achievement','difficulty','lvl','dx_score','sync', 'combo']
RecordEntryDict = dict[RecordEntryKeys, Optional[Union[str,int,float]]]

RECORD_URL_MAP = cast(dict[MaimaiDX.ChartDifficulty, str],
                      MaimaiDX.Routes.Record.value)


class MDXParser():
    """Parser class for MaimaiEXSession instances"""
    TIME_DELAY: Final[float] = 0.5
    debug: bool = False

    def __init__(self, session: MaimaiEXSession):
        """Initialises instance variables."""
        self.session = session
        self.records = []
        self.debug: bool = False

    async def fetch_record(self,difficulty: MaimaiDX.ChartDifficulty):
        """Fetches HTML of difficulty, route predefined."""
        return await self.session.get_html(route=RECORD_URL_MAP[difficulty])

    async def fetch_records(self, excl=None):
        """Fetches HTML from routes per difficulty predefined in module constants"""
        if not excl: excl = [None]
        if not getattr(self,'session',False):
            raise ValueError("Not attached to a session!")

        for difficulty in RECORD_URL_MAP.keys():
            if difficulty in excl: continue
            yield (difficulty, self.fetch_record(difficulty))
            await asyncio.sleep(self.TIME_DELAY)

    async def debug_fetch(self, excl=None):
        if not excl: excl = [None]

        for difficulty in get_args(MaimaiDX.ChartDifficulty):
            html_str = ''
            if difficulty in excl: continue
            try:
                with open(f'debug_data/{difficulty}.html', 'r') as f:
                    html_str = str(f.read())
            except OSError: pass
            async def _return_html():
                return html_str
            yield (difficulty, _return_html())

    async def parse_records(self, exclude=None):
        """
        Async generator, parses HTML responses
        Returns:
            record_entry_map (dict) = dict[diff,list[RecordEntry]]
        """
        if not exclude: exclude = [None]
        fetch = self.fetch_records if not getattr(self, 'debug', False) else self.debug_fetch
        async for diff, record in fetch(excl=exclude):
            record = await record
            soup = bs4.BeautifulSoup(record, "html.parser")
            res: list[RecordEntry] = []
            #record container
            diff_records = soup.find_all('div',attrs={'class':'w_450 m_15 p_r f_0'})
            for r in diff_records:
                record_entry: RecordEntryDict = {'type': None,
                                                 'song': None,
                                                 'difficulty': diff,
                                                 'lvl': 0,
                                                 'achievement': 0.0,
                                                 'sync': None,
                                                 'combo': None}
                rc = r.find('form') # type: ignore
                dx_std_img = r.find('img',recursive=False) # type: ignore

                if rc is not None and dx_std_img is not None:
                    if dx_std_img["src"] == 'https://maimaidx-eng.com/maimai-mobile/img/music_dx.png': # type: ignore
                        record_entry['type'] = 'DX'
                    else:
                        record_entry['type'] = 'STD'

                    lvl = rc.find('div',
                                  attrs={'class':'music_lv_block f_r t_c f_14'})
                    if lvl: lvl = lvl.text
                    else: lvl = '?'
                    record_entry['lvl'] = lvl

                    song = rc.find('div',
                                   attrs={'class':'music_name_block t_l f_13 break'})
                    if song: song = song.text
                    else: song = 'N/A'
                    record_entry['song'] = song

                    achievement = rc.find('div',
                                          attrs={'class':'music_score_block w_112 t_r f_l f_12'})
                    if achievement: achievement = achievement.text
                    else: achievement = '0.0'
                    record_entry['achievement'] = achievement

                    dx_score = rc.find('div',
                                       attrs={'class':'music_score_block w_190 t_r f_l f_12'})
                    if dx_score: dx_score = dx_score.text
                    else: dx_score = 'N/A'
                    record_entry['dx_score'] = dx_score

                    icons = rc.find_all('img',
                                        attrs={'class':'h_30 f_r'}, recursive=False)
                    combo: MaimaiDX.RecordCombo = ''
                    sync: MaimaiDX.RecordSync = ''

                    if len(icons) > 0:
                        if icons[0] and icons[0]['src']:
                            for sync_type in get_args(MaimaiDX.RecordSync):
                                if sync_type != '':
                                    if f'music_icon_{sync_type}' in icons[0]['src']:
                                        sync = sync_type
                        if len(icons) > 1:
                            if icons[1] and icons[1]['src']:
                                combo: MaimaiDX.RecordCombo = ''
                                for combo_type in get_args(MaimaiDX.RecordCombo):
                                    if combo_type != '':
                                        if f'music_icon_{combo_type}' in icons[1]['src']:
                                            combo = combo_type


                    if achievement != '0.0':
                        record_entry_class = RecordEntry(chart_type=record_entry['type'],difficulty=diff,achievement=achievement,song=song,lvl=lvl,sync=sync,combo=combo)
                        res.append(record_entry_class)

            yield diff,res






