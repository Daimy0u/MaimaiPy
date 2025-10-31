from session import MaimaiSession, MaimaiEXSession
import os
import asyncio

loop = asyncio.new_event_loop()
cookie = os.getenv('COOKIE','<COOKIE>')

async def simple_session_test():
    mai = MaimaiEXSession(cookie=cookie)
    await mai.get_data()
    print(mai.data)
    await mai.logout("/home/userOption","/logout/?")
    await mai.close()

if __name__ == "__main__":
    loop.run_until_complete(simple_session_test())
    

