import sys
import pathlib
from typing import List
from bs4 import BeautifulSoup
import asyncio
from aiohttp import ClientSession
sys.path.append(str(pathlib.Path(__file__).parent.parent.resolve()))
sys.path.append(str(pathlib.Path(__file__).parent.parent.parent.resolve()))
from model import db_query
from helper import get_web_page
from custom_exception import GetWebPageError
from kafka import KafkaProducer, errors

SOURCE = "PTT"

class pttUrlGetter():
    def __init__(self, is_first, target_board, producer):
        self.board_url = (
            f"https://www.ptt.cc/bbs/"
            f"{target_board}/index.html"
        )
        self.is_first = is_first
        self.target_board = target_board
        self.latest_url = None
        self.latest_page_index = ""
        self.url_list = []
        try:
            self.producer = producer
        except errors.BrokerNotAvailableError:
            raise errors.BrokerNotAvailableError

    def set_up(self):
        """Set up all attribute"""
        if not self.is_first:
            self.latest_url = self.get_latest_url_from_db()
    
        self.latest_page_index = self.get_latest_page_index()
        self.url_list = self.get_url_list()

    def send_to_kafka(self) -> None:
        """Send url list to kafka"""
        for url in self.url_list:
            self.producer.send(
                f"{SOURCE}_URL",
                url.encode("utf-8")
            )

    def get_latest_page_index(self) -> str:
        """
        Get the latest page index
        Returns:
            latest_page_index(str)
        """
        response = get_web_page(self.board_url)
        if response == "404":
            raise GetWebPageError(
                f"The PTT system did not have "
                f"board: {self.target_board}"
            )
        
        if response == "500":
            raise GetWebPageError(
                f"Internal Server Error of "
                f"{self.board_url}"
            )
        
        soup = BeautifulSoup(response, "html.parser")
        # Get the group of button
        btn = soup.select('div.btn-group > a')
        # Get the url of previous page
        up_page_href = btn[3]['href']
        # Add the previous-page-url into url
        next_page_url = (
            f"https://www.ptt.cc"
            f"{up_page_href}"
        )
        # Get the latest page index
        latest_page_index = next_page_url[next_page_url.find("index")+5:next_page_url.find(".html")]

        return latest_page_index

    def get_latest_url_from_db(self) -> str:
        """
        Get the latest url from DB
        Returns:
            latest_url(str)
        """
        return db_query.get_latest_url(SOURCE, self.target_board)

    def get_url_list(self) -> List[str]:
        """
        Get the url list of article 
        Returns:
            url_list(list)
        """

        url_list = []
        #def cancel_tasks():
        #    """Cancel all task of asyncio"""
        #    for task in asyncio.all_tasks():
        #        task.cancel()

        def get_hrefs(target_url: str):
            """
            Get the web page of target url then parse and get the URL of each article
            For the non-first time to get the board of PTT
            Args:
                target_url(str)
            """
            response = get_web_page(target_url)
            if response == "404":
                raise GetWebPageError(
                    f"The PTT system did not have "
                    f"{target_url}"
                )
            
            if response == "500":
                raise GetWebPageError(
                    f"Internal Server Error of "
                    f"{target_url}"
                )

            soup = BeautifulSoup(response, "html.parser")
            results = soup.select("div.title")

            if str(int(self.latest_page_index) + 1) in target_url:
                """
                if the latest page index exist in url
                we have to remove the rule, announcement page 
                """
                results = results[:-5]
            for item in results[::-1]:
                a_item = item.select_one("a")
                if a_item:
                    url = 'https://www.ptt.cc' + a_item.get('href')
                    # if get the latest url from web, then break
                    if url == target_url or (not self.is_first and url == self.latest_url): 
                        return False
                    url_list.append(url)

        async def get_hrefs_async(target_url: str, session: ClientSession) -> None:
            """
            Get the web page of target url then parse and get the URL of each article
            Args:
                target_url(str)
                session(ClientSession())
            """
            async with session.get(target_url) as response:
                html_body = await response.text()
                soup = BeautifulSoup(html_body, "html.parser")
                results = soup.select("div.title")
                for item in results:
                    a_item = item.select_one("a")
                    if a_item:
                        url = 'https://www.ptt.cc' + a_item.get('href')
                        # if get the latest url from web, then break
                        if url == target_url: 
                            continue
                        url_list.append(url)

        async def caller(latest_index: str):
            """
            Generate the async tasks by given latest index
            Args:
                latest_index(str): Latest index of page
            """
            if self.is_first:
                async with ClientSession() as session:
                    tasks = []
                    for index in range(int(latest_index) + 1, 0, -1):
                        tasks.append(
                            asyncio.create_task(
                                get_hrefs_async(
                                    f"""{self.board_url[:self.board_url.find("index")+5]}{index}.html""",
                                    session
                                )
                            )
                        )
                    await asyncio.gather(*tasks) 

            else:
                for index in range(int(latest_index) + 1, 0, -1):
                    target_url = (
                        f"""{self.board_url[:self.board_url.find("index")+5]}"""
                        f"""{index}.html"""
                    )
                    res = get_hrefs(target_url)
                    if not res:
                        break
                
                       
        asyncio.run(caller(self.latest_page_index))
        return url_list


