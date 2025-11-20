"""Provides parser classes as session-class instance wrappers."""
import bs4

import re
from typing import Optional, Literal, Final, Union, get_args, cast
import asyncio

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

    async def fetch_recent_record(self, **kwargs):
        recent = None
        if 'debug' in kwargs and 'debug_fp_recent_html'in kwargs:
            if kwargs['debug']:
                with open(kwargs['debug_fp_recent_html'], 'r+') as f:
                    recent = f.read()
            else:
                if not self.session.auth_status:
                    await self.session.login()
                recent = self.session.get_html(route=MaimaiDX.Routes.RecordData)

        if not isinstance(recent, str): raise TypeError()
        #recent = await recent
        soup = bs4.BeautifulSoup(recent, "html.parser")

        html_records = soup.find_all('div',attrs={'class':'p_10 t_l f_0 v_b'})

        for r in html_records:
            timestamp: Optional[str] = ''
            callback_url: Optional[str] = None
            record_entry = {'type': None,
                            'song': None,
                            'difficulty': None,
                            'lvl': 'N/A',
                            'achievement': "0.0",
                            'sync': '',
                            'combo': ''}
            meta = r.find_next('div',attrs={'class': 'sub_title t_c f_r f_11'})
            if meta:
                metas = meta.find_all('span', class_='v_b')
                if len(metas) > 1:
                    timestamp = metas[1].get_text()

            log_container = None
            #Find container
            for diff in get_args(MaimaiDX.ChartDifficulty):
                d_text = str(diff).lower()
                log_container = r.find('div', attrs={'class':f'playlog_{d_text}_container'})
                if log_container:
                    record_entry['difficulty'] = diff
                    break

            if log_container:
                song_text = log_container.find('div',attrs={'class':'basic_block m_5 m_t_17 m_r_60 p_5 p_l_10 f_13 break'})
                if not song_text: continue

                level = song_text.find('div', class_='music_lv_back m_3 m_b_0 f_r t_c f_14 p_a playlog_level_icon')
                if level:
                    record_entry['lvl'] = level.get_text(strip=True)
                    level.extract()
                record_entry['song'] = song_text.get_text(strip=True)

                main_container = log_container.find('div', class_='p_r f_0')
                if not main_container: continue

                #chart type
                img = main_container.find('img', class_='playlog_music_kind_icon')
                if img:
                    img_src = img.attrs['src']
                    if not img_src: continue
                    if img_src == 'https://maimaidx-eng.com/maimai-mobile/img/music_dx.png':
                        record_entry['type'] = 'DX'
                    else:
                        record_entry['type'] = 'STD'

                #achievement %
                achv_int = main_container.find('div', class_='playlog_achievement_txt t_r')
                if achv_int:
                    achv_dec = achv_int.find('span', attrs={'class':'f_20'})
                    if achv_dec:
                        record_entry['achievement'] = achv_int.text

                #combo/sync status
                combo, sync = '',''
                combo_sync = main_container.find_all('img',class_='h_35 m_5 f_l')
                if combo_sync:
                    for c_s_entry in combo_sync:
                        img_src = c_s_entry.attrs.get('src', None)
                        if not img_src: continue
                        for sync_type in get_args(MaimaiDX.RecordSync):
                            if 'sync_dummy.png' in img_src or 'fc_dummy.png' in img_src: break
                            if sync_type != '':
                                if f'{sync_type}.png' in img_src:
                                    sync = sync_type
                                    break
                        for combo_type in get_args(MaimaiDX.RecordCombo):
                            if 'sync_dummy.png' in img_src or 'fc_dummy.png' in img_src: break
                            if combo_type != '':
                                if f'{combo_type}.png' in img_src:
                                    combo = combo_type
                                    break
                record_entry['combo'] = combo
                record_entry['sync'] = sync

                callback_param = log_container.find('input', attrs={'name': 'idx', 'type': 'hidden'})
                if callback_param:
                    callback_value = str(callback_param.get('value'))
                    if callback_value:
                        cb_a, cb_b = callback_value.split(',')
                        callback_url = f"https://maimaidx-eng.com/maimai-mobile/record/playlogDetail/?idx={cb_a}%2C{cb_b}"

                #three key parameters (searchable)
                if not record_entry['type'] or not record_entry['difficulty'] or not record_entry['song']:
                    continue

                record = RecordEntry(song=record_entry['song'],
                                     chart_type=record_entry['type'],
                                     difficulty=record_entry['difficulty'],
                                     achievement=record_entry['achievement'],
                                     lvl=record_entry['lvl'],
                                     sync=record_entry['sync'],
                                     combo=record_entry['combo'])

                yield (timestamp, record, callback_url)

    #typing for fetch_user
    Username = Optional[str]
    Rating = Optional[int]
    Title = Optional[str]

    async def fetch_user(self) -> tuple[Username, Rating, Title]:
        user_html = await self.session.get_html(route=MaimaiDX.Routes.Home)

        if user_html:
            soup = bs4.BeautifulSoup(user_html, "html.parser")

            username = soup.find("div", attrs={"class": "name_block f_l f_16"})
            username = username.text if username else None

            rating = soup.find("div", attrs={"class": "rating_block"})
            rating = int(rating.text) if rating else None

            title = soup.find("div", attrs={"class": "trophy_inner_block f_13"})
            title = title.text.replace("\n", "") if title else None

            return username, rating, title

        return None, None, None























