from dotenv import load_dotenv

import logging
import os
import asyncio
from collections import deque

from app.core.session import MaimaiEXSession
from app.core.parser import MDXParser
from app.core.datasource import MDXDataSource,OtogeDB
from app.models.record import RecordEntry


class Server:
    def __init__(self):
        self.session_queue = deque()

    def
