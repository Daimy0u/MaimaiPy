import logging
import os
import asyncio

from app.session import MaimaiSession, MaimaiEXSession
from app.parser import MDXParser
from app.datasource import OtogeDB, MDXDataSource
from app.record import RecordEntry
from dotenv import load_dotenv

if not load_dotenv(): raise EnvironmentError("Failed to load .env")
loop = asyncio.new_event_loop()

async def simple_session_test():
    cookie = os.getenv('COOKIE',None)
    if not cookie:
        raise EnvironmentError("Failed to retrieve COOKIE from .env")

    logging.basicConfig(filename='test.log', level=logging.DEBUG)
    logger = logging.getLogger("Test")
    logger.info(f'Logger initialised from testing suite.')

    source = OtogeDB()
    RecordEntry.set_source(source)

    #test_source(source)

    mai = MaimaiEXSession(cookie=cookie)
    parse = MDXParser(mai)
    await mai.init_ssid()
    await mai.login()
    async for diff,records in parse.parse_records(exclude=['BASIC','ADVANCED']):
        print(f"Fetched diff={diff}, string dumping records:\n")
        for r in records:
            print(f"({r.chart_type}) {r.difficulty} {r.internal_level} | {r.song} | achv={r.achievement} rating={r.rating} sync={r.sync} combo={r.combo}")

    #log = await mai.logout("/home/userOption","/logout/?")
    # if not log: print("\n\nNOT LOGGED OUT")
    await mai.session.close()

def test_source(source: MDXDataSource):
    songs = source.get_song()
    if songs:
        for song_name, song_data in songs.items():
            print("-----------------------------------------")
            print(f"{song_name} by {song_data.get('artist','N/A')}")
            print(f"Category: {song_data.get('category','N/A')}\nBPM:{song_data.get('bpm','N/A')}")
            print(f"DX Chart: {source.get_sheet(song_name,'DX','EXPERT') is not None}")
            print(f"STD Chart: {source.get_sheet(song_name,'STD','EXPERT') is not None}")
            for t in ['DX','STD']:
                for d in ['ReMASTER','MASTER','EXPERT','ADVANCED','BASIC']:
                    res = source.get_sheet(song_name, t, d) # type: ignore
                    constant = source.get_constant(song_name,t,d) # type: ignore
                    if res and 'notes' in res and constant:
                        notes = res['notes']
                        if 'total' in res['notes']:
                            if 'designer' in res:
                                designer = res['designer']
                            else:
                                designer = 'N/A'
                            print(f'{d} ({t}) {constant} | designer={designer}:')
                            print(f'tap={notes["tap"]}, hold={notes["hold"]}, slide={notes["slide"]}, break={notes["break"]} / Total={res["notes"]["total"]}')
if __name__ == "__main__":
    loop.run_until_complete(simple_session_test())


