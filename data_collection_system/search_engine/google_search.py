import sys
import pathlib
import cloudscraper
import time
from aiohttp import ClientSession
import asyncio
import os
import hashlib 
from multiprocessing.dummy import Pool
sys.path.append(str(pathlib.Path(__file__).parent.parent.resolve()))
sys.path.append(str(pathlib.Path(__file__).parent.parent.parent.resolve()))
from google import search as google_search
from data_collection_system.tools.utils import get_cache_connection, get_proxy_ip
from data_collection_system.tools import log
from data_collection_system import ScraperAPI_proxy

DIR = f"""{str(pathlib.Path(__file__).parent.parent.resolve())}/file/"""
logger = log.create_logger()
NUM_WORKERS = 4

class googleEngine(searchEngine):
    def __init__(self, query_params):
        super().__init__()
        self.query_target = query_params['query_target']
        self.max_search_page = query_params['max_search_page']
        self.pause_time = query_params['pause_time']
        self.target_company_file_dir = query_params['target_company_file_dir']
        self.search_result_url_dir = query_params['search_result_url_dir']
        self.search_result_content_dir = query_params['search_result_content_dir']

    def get_search_url(self, keyword):
        try:
            return list(google_search(
                        f"""{keyword}{self.query_target}""", 
                        stop = self.max_search_page,
                        pause = self.pause_time, proxy = ScraperAPI_proxy)
                       )
        #若google因為too many connections擋掉，就從txt查找是否有紀錄
        except Exception as error:
            #logger.error(error)
            #if "Too Many Requests" in error:
                #return self.get_google_search_url_list_from_txt(keyword)
            logger.error(f"""get_search_url {error}""")

    def search(self):
        self.target_company_list = self.get_target_company_list_from_txt()        
        with Pool(NUM_WORKERS) as pool:
            pool.map(self.do_search, self.target_company_list)
            
            
    def do_search(self, company_name):
        url_list = self.get_search_url(company_name)
        if not url_list:
            return 
        
        self.save_url_list_to_txt(company_name, url_list)
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(self.caller(company_name, url_list))  

    async def caller(self, company_name, url_list):
        async with ClientSession() as session:
            tasks = [asyncio.create_task(self.get_web_content(session, company_name, url)) for url in url_list]  
            await asyncio.gather(*tasks)  # 打包任務清單及執行  
            
    async def get_web_content(self, session, company_name, url):
        try:
            async with session.get(url) as response:
                if response.status == 200:
                    web_content = await response.text()
                    logger.info(f"""{company_name} {url}""")
                    self.save_web_content_to_txt(web_content, url, company_name)
                else:
                    logger.info(f"""Failed to get response of {url} with status code {response.status}""")
        except asyncio.TimeoutError:
            logger.error(f"""get_web_content : {url} with asyncio timeout""")

        except Exception as error:
            logger.error(f"""get_web_content : {url} with {error}""")
            
    def get_google_search_url_list_from_txt(self, company_name):   
        try:
            with open(f"""{DIR}google_search_url_result/{company_name}_url_list.txt""") as f:
                return [line for line in f]
        except Exception as error:
            return []
  
if __name__ == '__main__':
    start_time = time.time()
    query_params = {
        "query_target" : "面試心得",
        "max_search_page" : 50,
        "pause_time" : 5,
        "target_company_file_dir" : f"""{DIR}company_list.txt""",
        "search_result_url_dir" : f"""{DIR}search_result/google_search_url_result/""",
        "search_result_content_dir" : f"""{DIR}search_result/google_search_content_result/""",
    }
    google = googleEngine(query_params)
    google.search()
    logger.info(f"The time consuming of google search is : {time.time() - start_time}")