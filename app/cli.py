import asyncio
import logging
import os
import math
import time
from typing import Optional
from blessed import Terminal
from dotenv import load_dotenv

from app.client.handler import OutputMessage,IOHandler, queue_output as io_print
from app.core.games.maimaidx import MaimaiDX
from app.core.session import MaimaiEXSession
from app.core.parser import MDXParser
from app.core.datasource import MDXDataSource, OtogeDB
from app.models.record import RecordEntry


class Client:
    io: IOHandler
    term = Terminal()
    cookie: Optional[str] = None
    source: MDXDataSource

    records: list[RecordEntry]


    def __init__(self, **kwargs):
        if 'cookie' in kwargs:
            cookie = kwargs['cookie']
        else:
            cookie = None
        self.io = IOHandler()
        self.cookie = self.load_cookie() if not cookie else cookie
        self.source = self.load_source()
        self.records = []
        asyncio.run(self.fetch_scores())


    def load_cookie(self):
        load_dotenv()
        env_cookie = os.getenv('COOKIE',None)
        if not env_cookie:
            raise EnvironmentError("Cookie not provided and not configured in .env")
        return env_cookie

    def load_source(self, datasource: Optional[type[MDXDataSource]] = None) -> MDXDataSource:
        if datasource:
            io_print(f"Data: initalising {datasource.__name__}...", location=(0,0),
                    flush=False)
            source = datasource()
        else:
            io_print(f"Data: initalising default (OtogeDB)...", location=(0,0),
                    flush=False)
            source = OtogeDB(useFull=True)

        n_songs, n_sheets = source.get_stats()
        io_print('', formatter=lambda term, _: term.clear_eol +
                                                'Data: ' +
                                                term.green2('Successfully fetched ') +
                                                term.bold(term.yellow2(f'{n_songs} ')) + 'songs and ' +
                                                term.bold(term.yellow2(f'{n_sheets} ')) +'sheets ' +
                                                f'from {source.__class__.__name__}.'
                    , location=(0,0),
                    flush=False)

        return source

    async def fetch_scores(self):
        if not self.source.ready:
            raise LookupError
        if not self.cookie:
            raise ValueError

        session = MaimaiEXSession(self.cookie)
        io_print(f"Session: initalising...", location=(0,1))
        await session.login()

        if session.auth_status:
            io_print("Session: ", formatter=lambda t, tx: tx +
                                                        t.clear_eol +
                                                        t.green2(t.bold('Success'))
                    ,location=(0,1))
            parser = MDXParser(session)

            #debug
            parser.debug = True
            await session.session.close()

            layout: dict[MaimaiDX.ChartDifficulty, tuple] = {
                "BASIC": ((0,3),(69, 193, 36)),
                "ADVANCED": ((0,4),(255, 186, 1)),
                "EXPERT": ((0,5),(255, 123, 123)),
                "MASTER": ((0,6),(159, 81, 220)),
                "ReMASTER": ((0,7), (219, 170, 255))
            }
            for d, (location, color) in layout.items():
                io_print('', location=location,
                         formatter=lambda t, _, diff=d, color=color: t.clear_eol +
                                                                     t.on_color_rgb(*color)(t.bold(t.white(diff))) +
                                                                     ' - ',
                    flush=False)

            async for diff, records in parser.parse_records():
                self.records.extend(records)

                location, color = layout[diff]
                location = len(diff) + 3, location[1]

                io_print('', location=location,
                             formatter=lambda t, _,
                                                color=color,
                                                count=len(records): 'Fetched ' +
                                                    t.bold(t.color_rgb(*color)(str(count))) +
                                                    ' records.',
                             flush=False)



def main():
    client = Client()

if __name__ == '__main__':
    main()
