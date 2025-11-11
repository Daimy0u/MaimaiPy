import logging
import os
import asyncio
from json import dumps as json_dump

from app.core.session import MaimaiEXSession
from app.core.parser import MDXParser
from app.core.datasource import OtogeDB, MDXDataSource
from app.models.record import RecordEntry
from app.database.db import Engine, get_engine, session_scope
from app.database.models import Base, Chart, Song

async def async_fetch_charts(song_title: str, song_data: dict):
    charts = []
    for chart_type in ['DX','STD']:
        if not song_data[song_title]['charts'][chart_type]: continue
        for difficulty in ['BASIC','ADVANCED','EXPERT','MASTER','ReMASTER']:
            if difficulty not in song_data[song_title]['charts'][chart_type]:
                continue
            chart = song_data[song_title]['charts'][chart_type][difficulty]
            if chart['internal'] == '':
                chart['internal'] = 0.0
            else:
                chart['internal'] = float(chart['internal'])
            chart_db = Chart(song_title = song_title,
                             chart_type=chart_type,
                             difficulty=difficulty,
                             level=chart['level'],
                             internal_constant=float(chart['internal']),
                             designer=chart['designer'],
                             notes=json_dump(chart['notes'],ensure_ascii=False))

            charts.append(chart_db)
    return charts

def db_init_sources(engine: Engine):
    source = OtogeDB()
    songs = source.get_song()
    if not songs: raise ValueError("Songs failed to initialise")

    with session_scope(engine) as session:
        for title in songs:
            charts = asyncio.run(async_fetch_charts(title, songs))
            song = Song(title = title,
                        version = songs[title]['version'],
                        title_kana = songs[title]['kana'],
                        artist = songs[title]['artist'],
                        category = songs[title]['category'],
                        bpm = songs[title]['bpm'],
                        image_url = songs[title]['image_url'],
                        wiki_url = songs[title]['wiki_url'],
                        charts = charts)

            session.add_all(charts + [song])

if __name__ == '__main__':
    engine = get_engine()
    Base.metadata.create_all(engine)
    db_init_sources(engine)









engine = get_engine()


Base.metadata.create_all(engine)



