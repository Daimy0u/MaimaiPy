from session import MaimaiSession, MaimaiEXSession
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
    await mai.get_data()
    print(mai.data)
    await mai.logout("/home/userOption","/logout/?")
    await mai.session.close()

if __name__ == "__main__":
    loop.run_until_complete(simple_session_test())
    

