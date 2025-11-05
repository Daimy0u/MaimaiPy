import json
import os
from dotenv import load_dotenv
import pytest
import asyncio
import pytest_asyncio
import aiohttp
from session import MaimaiEXSession


load_dotenv()
j = {
    "COOKIE": os.getenv('COOKIE', '')
}

@pytest.mark.asyncio
class TestSessionMaimai:
    @pytest_asyncio.fixture(autouse=True)
    async def fixture(self):
        await asyncio.sleep(0)
        if j["COOKIE"] != '': raise EnvironmentError("Failed to load .env")
        
        self.maimai = MaimaiEXSession(cookie=j["COOKIE"])
        try:
            yield
        finally:
            try:
                await self.maimai.session.close()
            except Exception:
                pass
        


    @pytest.mark.skipif(j["COOKIE"] == "<COOKIE-HERE>", reason="No default placeholder")
    @pytest.mark.xfail(reason="Cookies somehow revoked in some tests")
    async def test_init_ssid_good(self):
        while self.fixture:
            await self.maimai.init_ssid()
            assert getattr(self.maimai,'ssid',False)

    @pytest.mark.skipif(j["COOKIE"] == "<COOKIE-HERE>", reason="No default placeholder")
    @pytest.mark.xfail(reason="Cookies somehow revoked in some tests")
    async def test_init_ssid_bad(self):
        with pytest.raises(IndexError):
            await self.maimai.init_ssid()
            assert getattr(self.maimai,'ssid',True)


    @pytest.mark.skipif(j["COOKIE"] == "<COOKIE-HERE>", reason="No default placeholder")
    @pytest.mark.xfail(reason="Cookies somehow revoked in some tests")
    async def test_login_cookies_double_login(self):
        await self.maimai.init_ssid()
        await self.maimai.login()
        new_session = MaimaiEXSession(cookie=j["COOKIE"])
        
        with pytest.raises(RuntimeWarning):
            assert self.maimai.auth_status is True
            await new_session.init_ssid()
            await new_session.login()
            assert await new_session.login() is True
        
        await new_session.session.close()

