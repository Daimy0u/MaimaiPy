from enum import EnumMeta, Enum
import re
from typing import Union, cast, Optional
from datetime import datetime
import aiohttp
import asyncio
from bs4 import BeautifulSoup, Tag
from bs4.element import NavigableString
#from models import MaimaiTrack, MaimaiUser
from typing_extensions import Final, LiteralString
from urllib.parse import urlparse, parse_qs
from copy import deepcopy


__all__ = ["MaimaiSession"]
Params = dict[str,str]
PageParams = dict[str,Params]

class PageRouteMeta(EnumMeta):
    def __getitem__(self, name):
        try:
            return super().__getitem__(name)
        except (TypeError, KeyError) as error:
            raise error
    def __iter__(self):
        return super().__iter__()
            
class PageRoutes(Enum, metaclass=PageRouteMeta):
    HOME: str
    PLAYER: str
    RECORDS: str
    USER_OPTION: str

class MaimaiEX(PageRoutes):
    HOME = '/home'
    PLAYER = '/playerData'
    RECORDS = '/record'
    USER_OPTION = '/home/userOption'
    
AUTH_CONDITIONS: Final[dict] = {
                                    "maimaidxex": {
                                        False: set(['Login|maimai DX NET','maimai DX NET－Error－'])
                                    }
                                }
Pages: Final[PageParams] = {
                        "maimaidxex": {
                            "site_id": "maimaidxex",
                            "redirect_url": "https://maimaidx-eng.com/maimai-mobile",
                            "back_url": "https://maimai.sega.com/",
                         }
                        }
    
class ALLNETSessionWithCookie():
    _AUTH_URL: Final[LiteralString] = 'https://lng-tgk-aime-gw.am-all.net/common_auth/login'
    _URL_PARAMS: Final[PageParams] = Pages
    
    def __init__(self, *, clal_cookie: str, page: str, page_routes: type[PageRoutes]):
        if not self._URL_PARAMS.get(page, False):
            raise ValueError(f'ALLNETSessionWithCookie: page {page} is an invalid argument.')
        else:
            self.url_params: Final[dict] = self._URL_PARAMS[page]
        
        self.routes = page_routes
        self.is_logged_in: bool = False
        self.cookie = clal_cookie
        self.headers: dict = {
            "Content-Type": "application/x-www-form-urlencoded",
            "Connection": "keep-alive",
        }
        self.session = aiohttp.ClientSession(headers=self.headers)
    
    async def init_ssid(self,cookie_override: Optional[str] = None) -> str:
        if cookie_override is not None:
            self.session.cookie_jar.update_cookies({"clal": cookie_override})
        else:
            self.session.cookie_jar.update_cookies({"clal": self.cookie})
            
        async with self.session.get(self._AUTH_URL, 
                               allow_redirects=True, 
                               params=self.url_params) as response:
            try:
                if len(response.history) > 0:
                    redirect_queries = response.history[1].url.query
                    if redirect_queries.get('ssid', False):
                        self.ssid = redirect_queries['ssid']
                        return self.ssid
            except (IndexError, AttributeError, KeyError):
                raise ConnectionRefusedError("Invalid authorisation cookie, possibly wrong or revoked.")
        
        raise ValueError("SSID not obtainable, is cookie still valid?")
            
    async def login(self, ssid_override: Optional[str] = None):
        if ssid_override is not None:
            ssid = ssid_override
        elif not self.ssid:
            ssid = self.init_ssid()
            await ssid
        else:
            ssid = self.ssid
            
        
        #todo find better way to store this
        async with self.session.get(self.url_params['redirect_url'], params={"ssid": ssid}) as response:
            text = await response.text()
            soup = BeautifulSoup(text, "html.parser")
            title = [*soup.find_all("title")][0].text

            auth_fail = AUTH_CONDITIONS.get(self.url_params['site_id'],{}).get(False,None)
            
            if auth_fail and title not in auth_fail:
                self.auth_status = True
                return self.auth_status
            elif auth_fail and title in auth_fail:
                return False
            else:
                return ValueError("Invalid auth condition configuration!")
            
    async def logout(self, referer: str, logout_route: str) -> bool:
        """'Log-out' from the session. Returns True if logged out successfully."""
        if not self.auth_status: return False
        url = self.url_params["redirect_url"]
        if not referer or not logout_route:
            raise RuntimeError("Logout method not provided!")
        else:
            referer= f'{url}{referer}'
        
        logout_success: bool = False
        self.session.headers["Referer"] = referer
        await self.session.get(f'{referer}{logout_route}')
        
        async with self.session.get(self.url_params['redirect_url']) as response:
            text = await response.text()
            soup = BeautifulSoup(text, "html.parser")
            title = soup.find("title")
            if title: title = title.text
            else: title = ''
            logout_success = title in AUTH_CONDITIONS.get(self.url_params['site_id'],{}).get(False,None)
            
        self.auth_status = not logout_success
        return logout_success

    async def get_html(self, route: Union[str, PageRoutes], **kwargs):
        if isinstance(route, PageRoutes):
            path = route.value
        elif isinstance(route, str):
            try:
                path = cast(PageRoutes, self.routes[route]).value
            except Exception:
                path = route
        else:
            raise TypeError("invalid route parameter: must be an instance of str or PageRoutes")

        url = f"{self.url_params['redirect_url']}{path}"
        
        params = {"ssid": getattr(self, "ssid", None)} if getattr(self, "ssid", None) else None
        
        async with self.session.get(url, params=params, **kwargs) as response:
            return await response.text()

class MaimaiEXSession(ALLNETSessionWithCookie):
    DATA_FETCH_LIST: Final[list[str]] = ['PLAYER','RECORDS']
    DATA_PROTOTYPE: Final[dict] = {
        "PLAYER": {"timestamp": 0, "html": None},
        "RECORDS": {},
    }

    def _instance_copy(self) -> dict:
        # deep-copy to avoid shared mutable state between instances
        return deepcopy(self.DATA_PROTOTYPE)

    def __init__(self, cookie: str):
        super().__init__(clal_cookie=cookie, page='maimaidxex', page_routes=MaimaiEX)
        self.data = self._instance_copy()
    
    async def check_auth(self) -> bool:
        if not getattr(self, "auth_status", False):
            await self.init_ssid()
            auth = self.login()
            await auth
            self.auth_status = bool(auth)
        return self.auth_status
        
    async def get_all_data(self):
        if not self.check_auth(): raise ValueError("Auth Error")
        
        await asyncio.sleep(5)
        for data_label in self.data.keys():
            html = await self.get_html(data_label)
            print(html)
            self.data[data_label]["html"] = html
            self.data[data_label]["timestamp"] = datetime.now().timestamp()
            await asyncio.sleep(10)
    
    async def get_data(self) -> str:
        auth = await self.check_auth()
        if not auth: raise ValueError("Auth Fail")
        
        html = await self.get_html('RECORDS')
        
        self.data['RECORDS']["html"] = html
        self.data['RECORDS']["timestamp"] = datetime.now().timestamp()

        return html

class MaimaiSession:
    """Basic maimaiDX client session, I hope it works."""

    def __init__(self, *, ssid: str = ""):
        """Create a session for this maimai instance."""
        self.is_logged_in: bool = False
        self.ssid: str = ssid
        self.headers: dict = {
            "Content-Type": "application/x-www-form-urlencoded",
            "Connection": "keep-alive",
        }
        self.session: aiohttp.ClientSession = aiohttp.ClientSession(headers=self.headers)
        self.AUTH_URL: Final[LiteralString] = "https://lng-tgk-aime-gw.am-all.net/common_auth/login"
        self.HOME_URL: Final[LiteralString] = "https://maimaidx-eng.com/maimai-mobile"

    async def get_ssid_from_credentials(self, *, username: str, password: str) -> None:
        """Create a NEW SSID from given SEGA ID username **AND PASSWORD**"""
        async with self.session.get(
            self.AUTH_URL,
            params={
                "site_id": "maimaidxex",
                "redirect_url": self.HOME_URL,
                "back_url": "https://maimai.sega.com/",
            },
        ):
            pass

        async with self.session.post(
            f"{self.AUTH_URL}/sid",
            data={
                "retention": 1,
                "sid": username,
                "password": password,
            },
        ) as response:
            url_with_ssid = response.history[1].url.human_repr()
            self.ssid = self._parse_ssid(url_with_ssid)

    async def get_ssid_from_cookie(self, *, cookie: str) -> None:
        """Create a NEW SSID from given cookie"""
        # Set the cookie in the session's cookie jar
        self.session.cookie_jar.update_cookies({"clal": cookie})

        async with self.session.get(
            self.AUTH_URL,
            params={
            "site_id": "maimaidxex",
            "redirect_url": self.HOME_URL,
            "back_url": "https://maimai.sega.com/",
            },
        ) as response:
            try:
                url_with_ssid = response.history[1].url.human_repr()
            except IndexError:
                raise ValueError("Invalid account provided")

            self.ssid = self._parse_ssid(url_with_ssid)

    def _parse_ssid(self, url: str) -> str:
        if not url:
            raise ValueError("You passed an invalid URL")

        ssid = url[len(f"{self.HOME_URL}?ssid=") :]

        if ssid:
            return ssid
        else:
            raise ValueError(f"Unable to retrieve SSID from {url}")

    async def login(self) -> bool:
        """'Log-in' from a maimai instance. Returns True if logged in successfully"""
        if not self.ssid:
            raise ValueError(
                "You did not create a valid SSID, you can solve this by calling create_ssid_from_credentials "
                "or create_ssid_from_cookie or pass in the constructor"
            )

        if self.is_logged_in:
            raise RuntimeWarning("You already logged in")

        async with self.session.get(self.HOME_URL, params={"ssid": self.ssid}) as response:
            text = await response.text()
            soup = BeautifulSoup(text, "html.parser")
            title = [*soup.find_all("title")][0].text

            if title != "maimai DX NET－Error－":  # I know that '-' is an Unicode
                self.is_logged_in = True
                return self.is_logged_in
            else:
                return False

    async def logout(self) -> bool:
        """'Log-out' from the session. Returns True if logged out successfully."""
        self.must_be_logged_in()

        self.session.headers["Referer"] = "https://maimaidx-eng.com/maimai-mobile/home/userOption/"
        is_logged_out: bool = False

        async with self.session.get(f"{self.HOME_URL}/home/userOption/logout/?"):
            pass

        async with self.session.get(self.HOME_URL) as response:
            text = await response.text()
            soup = BeautifulSoup(text, "html.parser")
            title = [*soup.find_all("title")][0].text
            is_logged_out = title == "Login|maimai DX NET"

        self.is_logged_in = not is_logged_out
        return is_logged_out

    async def close_session(self) -> None:
        if self.is_logged_in:
            raise RuntimeWarning("You are logged in, you sure that you wanna close the session?")

        await self.session.close()

    def must_be_logged_in(self) -> None:
        if not self.is_logged_in:
            raise RuntimeError("This session is not logged in")

    async def get_html(self, method: str, url: str, **kwargs) -> str:
        """Perform HTTP request and return the url"""
        async with self.session.request(method=method, url=url, **kwargs) as response:
            return await response.text()

    def get_tag(self, html: str, tag_name: str, attr: dict) -> Union[Tag, NavigableString]:
        """Find html text with given tag name and attributes"""
        soup = BeautifulSoup(html, "html.parser")
        result = soup.find(tag_name, attr)

        if not result:
            error_tag = Tag(name="ERROR")
            return error_tag

        return result

    async def resolve_user_data(self):
        self.must_be_logged_in()
        user_html = await self.get_html("GET", f"{self.HOME_URL}/home")

        username = self.get_tag(user_html, "div", {"class": "name_block f_l f_16"}).text
        rating: int = int(self.get_tag(user_html, "div", {"class": "rating_block"}).text)
        title = self.get_tag(user_html, "div", {"class": "trophy_inner_block f_13"}).text.replace("\n", "")

        title_rarity = self.get_tag(user_html, "div", {"class": re.compile(r"trophy_block trophy_([a-zA-Z]*) p_3 t_c f_0")}
        )["class"][1][ # type: ignore
            len("trophy_") :
        ]  # pyright: ignore

        stars = self.get_tag(user_html, "div", {"class": "p_l_10 f_l f_14"}).text

        dan_level_image_url = self.get_tag(user_html, "img", {"class": "h_35 f_l"})["src"][0]  # pyright: ignore

        season_level_image_url = self.get_tag(user_html, "img", {"class": "p_l_10 h_35 f_l"})["src"][ # type: ignore
            0
        ]  # pyright: ignore

        avatar_url = self.get_tag(user_html, "img", {"class": "w_112 f_l"})["src"][0]  # pyright: ignore

        tour_leader_image_url = self.get_tag(user_html, "img", {"class": "w_120 m_t_10 f_r"})["src"][ # type: ignore
            0
        ]  # pyright: ignore

        user_data_html = await self.get_html("GET", f"{self.HOME_URL}/playerData")
        playcount: str = self.get_tag(user_data_html, "div", {"class": "m_5 m_t_10 t_r f_12"}).text

        user_data = [
            username,
            rating,
            title,
            title_rarity,
            stars,
            tour_leader_image_url,
            dan_level_image_url,
            season_level_image_url,
            avatar_url,
            playcount,
        ]

        print(user_data)#.__dict__)

        return user_data

    def resolve_play_data(self):
        self.must_be_logged_in()
        return None
