from session import MaimaiEXSession
from app.record import RecordEntry
import asyncio
import bs4
from typing import Literal, Final, Union

MDXDifficulty = Literal['ReMASTER', 'MASTER', 'EXPERT', 'ADVANCED','BASIC']
RecordEntryKeys = Literal['type','song','achievement','difficulty','lvl','raw']
RecordEntryDict = dict[RecordEntryKeys,Union[str,int,float,None]]

RECORD_URL_MAP: dict[MDXDifficulty,str] = {
    'ReMASTER':'/record/musicGenre/search/?genre=99&diff=4',
    'MASTER':'/record/musicGenre/search/?genre=99&diff=3',
    'EXPERT':'/record/musicGenre/search/?genre=99&diff=2',
    'ADVANCED': '/record/musicGenre/search/?genre=99&diff=1',
    'BASIC':'/record/musicGenre/search/?genre=99&diff=0'
}


class MDXParser():
    TIME_DELAY: Final[float] = 6.0

    def __init__(self, session: MaimaiEXSession):
        self.session = session
        self.records = []

    async def fetch_record(self,difficulty: MDXDifficulty):
        return await self.session.get_html(route=RECORD_URL_MAP[difficulty])

    async def fetch_records(self, excl=None):
        if not excl: excl = [None]
        if not getattr(self,'session',False):
            raise ValueError("Not attached to a session!")

        for difficulty in RECORD_URL_MAP.keys():
            if difficulty in excl: continue
            yield (difficulty, self.fetch_record(difficulty))
            await asyncio.sleep(self.TIME_DELAY)

    async def parse_records(self, excl=None):
        if not excl: excl = [None]
        async for diff, record in self.fetch_records(excl=excl):
            soup = bs4.BeautifulSoup(await record, "html.parser")
            res: list[RecordEntry] = []
            #record container
            diff_records = soup.find_all('div',attrs={'class':'w_450 m_15 p_r f_0'})
            for r in diff_records:
                if r:
                    record_entry: RecordEntryDict = {'type': None, 'song': None, 'difficulty': diff, 'lvl':0, 'achievement': 0.0, 'raw': None}
                    #record_entry['raw'] = r.text
                    rc = r.find('form') # type: ignore
                    dx_std_img = r.find('img',recursive=False) # type: ignore
                
                    if rc is not None and dx_std_img is not None:
                        if dx_std_img["src"] == 'https://maimaidx-eng.com/maimai-mobile/img/music_dx.png': # type: ignore
                            record_entry['type'] = 'DX'
                        else:
                            record_entry['type'] = 'STD'
                            
                        lvl = rc.find('div',attrs={'class':'music_lv_block f_r t_c f_14'})
                        if lvl: lvl = lvl.text
                        else: lvl = '?'
                        record_entry['lvl'] = lvl
                        
                        song = rc.find('div',attrs={'class':'music_name_block t_l f_13 break'})
                        if song: song = song.text
                        else: song = 'N/A'
                        record_entry['song'] = song
                        
                        achievement = rc.find('div',attrs={'class':'music_score_block w_112 t_r f_l f_12'})
                        if achievement: achievement = achievement.text
                        else: achievement = '0.0'
                        record_entry['achievement'] = achievement
                        
                        if achievement != '0.0':
                            record_entry_class = RecordEntry(chart_type=record_entry['type'],difficulty=diff,achievement=achievement,song=song,lvl=lvl)
                            res.append(record_entry_class)
                
            yield diff,res
        
        
        
        

        
