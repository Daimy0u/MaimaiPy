from session import MaimaiSession, MaimaiEXSession
from parser import MDXParser
from dotenv import load_dotenv
import os
import asyncio
if not load_dotenv(): raise EnvironmentError("Failed to load .env")
loop = asyncio.new_event_loop()

async def simple_session_test():
    cookie = os.getenv('COOKIE',None)
    if not cookie:
        raise EnvironmentError("Failed to retrieve COOKIE from .env")
    
    mai = MaimaiEXSession(cookie=cookie)
    parse = MDXParser(mai)
    await mai.init_ssid()
    await mai.login()
    async for diff,records in parse.parse_records(excl=['BASIC','ADVANCED']):
        print(f"Fetched diff={diff}, string dumping records:\n")
        for r in records:
            print(f"({r.chart_type}) {r.difficulty} | {r.song} | achv={r.achievement} rating={r.rating}")
        
    #log = await mai.logout("/home/userOption","/logout/?")
   # if not log: print("\n\nNOT LOGGED OUT")
    await mai.session.close()

if __name__ == "__main__":
    loop.run_until_complete(simple_session_test())
    

