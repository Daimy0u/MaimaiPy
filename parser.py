from enum import Enum
from session import ALLNETSessionWithCookie,MaimaiEXSession
# References obtained from myjian's mai-tools
import asyncio
import bs4
from typing import Literal, Final

MDXDifficulty = Literal['ReMASTER', 'MASTER', 'EXPERT', 'ADVANCED','BASIC']

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
    
    async def fetch_records(self):
        if not getattr(self,'session',False):
            raise ValueError("Not attached to a session!")
        
        for difficulty in RECORD_URL_MAP.keys():
            yield (difficulty, self.fetch_record(difficulty))
            await asyncio.sleep(self.TIME_DELAY)
    
    async def parse_record(self):
        async for diff, record in self.fetch_records():
            soup = bs4.BeautifulSoup(await record, "html.parser")
            res = []
            #record container
            diff_records = soup.find_all('div',attrs={'class':'w_450 m_15 p_r f_0'})
            for r in diff_records:
                record = {'type': None, 'song': None, 'diff': diff, 'lvl':0, 'achievement': 0.0}
                if r is None: continue
                rc: ResultSet[Tag] = r.find_first_child('form') # type: ignore
                dx_std_img: ResultSet[Tag] = r.find_first_child('img') # type: ignore
                
                if rc is not None and dx_std_img is not None:
                    if dx_std_img.source == 'https://maimaidx-eng.com/maimai-mobile/img/music_dx.png':
                        record['type'] = 'DX'
                    else:
                        record['type'] = 'STD'

                    for rc_c in rc.find_all():
                        
                        
                        
            
            
            
            
        
    async def parse_records(self):
        self.records = [record async for record in self.fetch_records()]
        
        
        
        

        
