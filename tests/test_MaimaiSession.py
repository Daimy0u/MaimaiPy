import json
import os
import pytest
import asyncio
import pytest_asyncio
import aiohttp
from session import MaimaiSession


j = {
    "SID": os.getenv('SESSION_ID','<SID-HERE>'),
    "PWD": os.getenv('PASSWORD', '<PWD-HERE>'),
    "COOKIE": os.getenv('COOKIE', '<COOKIE-HERE>')
}

@pytest.mark.asyncio
class TestMaiMaiSession:
    @pytest_asyncio.fixture(autouse=True)
    async def fixture(self):
        await asyncio.sleep(0)
        self.maimai = MaimaiSession()
        try:
            yield
        finally:
            # make best-effort cleanup so tests don't leak sessions
            try:
                await self.maimai.close_session()
            except Exception:
                pass
        
        
       
    async def test_default_session(self):
        assert self.maimai.session is not None
        assert self.maimai.headers is not None
        assert self.maimai.ssid == ""

    async def test__parse_ssid_good(self):
        assert (
            self.maimai._parse_ssid("https://maimaidx-eng.com/maimai-mobile?ssid=abcdefghijklmnopqrstuxwxyz")
            == "abcdefghijklmnopqrstuxwxyz"
        )
    @pytest.mark.skipif(
        j["SID"] == "<SID-HERE>" or j["PWD"] == "<PWD-HERE>",
        reason="No default placeholder",
    )
    async def test_get_ssid_from_credentials_good(self):
        await self.maimai.get_ssid_from_credentials(username=j["SID"], password=j["PWD"])

    async def test_get_ssid_from_credentials_bad(self):
        with pytest.raises(IndexError):
            await self.maimai.get_ssid_from_credentials(username="YwY", password="OwO")

    @pytest.mark.skipif(j["COOKIE"] == "<COOKIE-HERE>", reason="No default placeholder")
    @pytest.mark.xfail(reason="Cookies somehow revoked in some tests")
    async def test_get_ssid_from_cookie_good(self):
        while self.fixture:
            await self.maimai.get_ssid_from_cookie(cookie=j["COOKIE"])

    @pytest.mark.skipif(j["COOKIE"] == "<COOKIE-HERE>", reason="No default placeholder")
    @pytest.mark.xfail(reason="Cookies somehow revoked in some tests")
    async def test_get_ssid_from_cookie_bad(self):
        with pytest.raises(IndexError):
            await self.maimai.get_ssid_from_cookie(cookie="abc")

    @pytest.mark.skipif(j["COOKIE"] == "<COOKIE-HERE>", reason="No default placeholder")
    @pytest.mark.xfail(reason="Cookies somehow revoked in some tests")
    async def test_login_cookie_good(self):
        await self.maimai.get_ssid_from_cookie(cookie=j["COOKIE"])
        await self.maimai.resolve_user_data()
        assert await self.maimai.login() is True
        

    @pytest.mark.skipif(j["COOKIE"] == "<COOKIE-HERE>", reason="No default placeholder")
    @pytest.mark.xfail(reason="Cookies somehow revoked in some tests")
    async def test_login_cookie_bad(self):
        with pytest.raises(IndexError):
            await self.maimai.get_ssid_from_cookie(cookie="abc")
            await self.maimai.login()

    @pytest.mark.skipif(
        j["SID"] == "<SID-HERE>" or j["PWD"] == "<PWD-HERE>",
        reason="No default placeholder",
    )
    async def test_login_credentials_good(self):
        await self.maimai.get_ssid_from_credentials(username=j["SID"], password=j["PWD"])
        assert await self.maimai.login() is True

    async def test_login_bad_ssid_provide(self):
        self.maimai = MaimaiSession(ssid="123")
        assert await self.maimai.login() is False

    async def test_login_bad_no_ssid(self):
        with pytest.raises(ValueError):
            await self.maimai.login()

    async def test_logout_no_login(self):
        with pytest.raises(RuntimeError):
            assert await self.maimai.logout() is True

    @pytest.mark.skipif(
        j["SID"] == "<SID-HERE>" or j["PWD"] == "<PWD-HERE>",
        reason="No default placeholder",
    )
    async def test_login_credentials_double_login(self):
        await self.maimai.get_ssid_from_credentials(username=j["SID"], password=j["PWD"])

        with pytest.raises(RuntimeWarning):
            assert await self.maimai.login() is True
            await self.maimai.login()

    @pytest.mark.skipif(j["COOKIE"] == "<COOKIE-HERE>", reason="No default placeholder")
    @pytest.mark.xfail(reason="Cookies somehow revoked in some tests")
    async def test_login_cookies_double_login(self):
        await self.maimai.get_ssid_from_cookie(cookie=j["COOKIE"])

        with pytest.raises(RuntimeWarning):
            assert await self.maimai.login() is True
            await self.maimai.login()

    @pytest.mark.skipif(
        j["SID"] == "<SID-HERE>" or j["PWD"] == "<PWD-HERE>",
        reason="No default placeholder",
    )
    async def test_login_credentials_login_double_logout(self):
        await self.maimai.get_ssid_from_credentials(username=j["SID"], password=j["PWD"])

        with pytest.raises(RuntimeError):
            assert await self.maimai.login() is True
            assert await self.maimai.logout() is True
            await self.maimai.logout()

    @pytest.mark.skipif(j["COOKIE"] == "<COOKIE-HERE>", reason="No default placeholder")
    @pytest.mark.xfail(reason="Cookies somehow revoked in some tests")
    async def test_login_cookies_login_double_logout(self):
        await self.maimai.get_ssid_from_cookie(cookie=j["COOKIE"])

        with pytest.raises(RuntimeWarning):
            assert await self.maimai.login() is True
            assert await self.maimai.logout() is True
            await self.maimai.logout()

    @pytest.mark.skipif(
        j["SID"] == "<SID-HERE>" or j["PWD"] == "<PWD-HERE>",
        reason="No default placeholder",
    )
    async def test_one_session_credentials(self):
        await self.maimai.get_ssid_from_credentials(username=j["SID"], password=j["PWD"])

        assert self.maimai.session.closed is False

        assert await self.maimai.login() is True
        assert await self.maimai.logout() is True
        await self.maimai.close_session()

        assert self.maimai.session.closed is True

    @pytest.mark.skipif(j["COOKIE"] == "<COOKIE-HERE>", reason="No default placeholder")
    @pytest.mark.xfail(reason="Cookies somehow revoked in some tests")
    async def test_one_session_cookie(self):
        await self.maimai.get_ssid_from_cookie(cookie=j["COOKIE"])

        assert self.maimai.session.closed is False

        assert await self.maimai.login() is True
        assert await self.maimai.logout() is True
        await self.maimai.close_session()

        assert self.maimai.session.closed is True

    @pytest.mark.skipif(
        j["SID"] == "<SID-HERE>" or j["PWD"] == "<PWD-HERE>",
        reason="No default placeholder",
    )
    async def test_login_credentials_close_session(self):
        with pytest.raises(RuntimeWarning):
            await self.maimai.get_ssid_from_credentials(username=j["SID"], password=j["PWD"])
            assert await self.maimai.login() is True
            await self.maimai.close_session()

    @pytest.mark.skipif(j["COOKIE"] == "<COOKIE-HERE>", reason="No default placeholder")
    @pytest.mark.xfail(reason="Cookies somehow revoked in some tests")
    async def test_login_cookie_close_session(self):
        with pytest.raises(RuntimeWarning):
            await self.maimai.get_ssid_from_cookie(cookie=j["COOKIE"])
            assert await self.maimai.login() is True
            await self.maimai.close_session()
