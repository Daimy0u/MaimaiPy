import matplotlib.pyplot as plt

import logging
import os
import json
import asyncio

from typing import Optional

from app.core.session import MaimaiEXSession
from app.core.parser import MDXParser
from app.core.statistics import StatisticalCollection, scatterplot
from app.core.datasource import OtogeDB, OtogeDBJPEX, MDXDataSource
from app.models.record import RecordEntry, RecordCollection
from app.core.utils.log import configure_logger
from dotenv import load_dotenv

if not load_dotenv(): raise EnvironmentError("Failed to load .env")
loop = asyncio.new_event_loop()

logging.basicConfig(filename='test.log', level=logging.DEBUG)
logger = logging.getLogger("Test")
logger.info(f'Logger initialised from testing suite.')

async def simple_session_test():
    configure_logger()
    cookie = os.getenv('COOKIE',None)
    if not cookie:
        raise EnvironmentError("Failed to retrieve COOKIE from .env")

    logging.basicConfig(filename='test.log', level=logging.DEBUG)
    logger = logging.getLogger("Test")
    logger.info(f'Logger initialised from testing suite.')

    source = OtogeDB(useFull=True)
    OtogeDBJPEX()
    RecordEntry.set_source(source)

    #test_source(source)

    mai = MaimaiEXSession(cookie=cookie)
    parse = MDXParser(mai)
    await mai.login()

    collection = RecordCollection()
    async for diff,records in parse.parse_records(exclude=['BASIC','ADVANCED']):
        print(f"Fetched diff={diff}")
        for r in records:
            collection.add(r)
    with open('collection_dump.txt', 'w+') as f:
        f.write(str(collection))

    await test_statistics(collection)
    await test_import(import_string=str(collection), same_comparison=collection)

    #log = await mai.logout("/home/userOption","/logout/?")
    # if not log: print("\n\nNOT LOGGED OUT")
    await mai.session.close()

async def test_import(filename: Optional[str] = None,
                      import_string: Optional[str] = None,
                      same_comparison: Optional[RecordCollection] = None) -> bool:
    record_collection = RecordCollection()
    if filename:
        with open(filename, 'r') as f:
            record_collection.from_str(f.read())
    elif import_string:
        record_collection.from_str(import_string)
    else:
        raise ValueError("Invalid parameters for import test.")


    if record_collection.record_map and same_comparison:
        (i0, i1, i2), diff = same_comparison.compare(record_collection)
        if (i0, i1, i2) != (0,0,0):
            logger.debug('IMPORT FAIL: Collection has difference: %s', str([(r.song, d) for r, d in diff]))
            return False
        return True

    if record_collection.record_map and not same_comparison:
        return True

    return False

async def test_statistics(collection: RecordCollection):
    stat = StatisticalCollection(collection)
    scatter = scatterplot(stat, 'rating', 'level_internal')
    if scatter: plt.show()








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


