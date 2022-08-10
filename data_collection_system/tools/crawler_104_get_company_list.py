import cloudscraper
import json
import asyncio
from aiohttp import ClientSession
from utils import get_cache_connection
import log

logger = log.create_logger()


TARGET_URL =  f'https://www.104.com.tw/company/ajax/list?'
 
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.92 Safari/537.36',
    'Referer': f"""https://www.104.com.tw/company/ajax/"""
}

def get_page_number(emp, indcat):
    """
    utility : get the max page under the given query condiction
    """
    query = f"""jobsource=checkc&indcat={indcat}&page=1&order=1&mode=s&emp={emp}"""
    url = TARGET_URL + query
    scraper = cloudscraper.create_scraper()
    response = scraper.get(url, headers=headers)
    if response.status_code != 200:
        return 0
    return response.json()['metadata']['pagination']['lastPage']

async def caller(emp, indcat):
    async with ClientSession() as session:
        tasks = [asyncio.create_task(get_company_list_from_104(page, session, emp, indcat)) for page in range(1, get_page_number(emp, indcat) + 1 )]   #建立任務清單
        await asyncio.gather(*tasks)  # 打包任務清單及執行
        
async def get_company_list_from_104(target_page, session, emp, indcat):
    try:
        query = f"""jobsource=checkc&indcat={indcat}&page={target_page}&order=1&mode=s&emp={emp}"""
        url = TARGET_URL + query
        async with session.get(url, headers=headers) as response:
            data = await response.json()
            cache_connection = get_cache_connection()
            for d in data['data']:
                cache_connection.sadd("COMPANY_LIST", d['name']) 
            
    except asyncio.TimeoutError:
        logger.error(f"""get_company_list_from_104 page: {target_page} with asyncio timeout""")
        
    except Exception as error:
        logger.error(f"""get_company_list_from_104 page: {target_page} with error""")
        
def get_104_crawler():
    cache_connection = get_cache_connection()
    cache_connection.delete("COMPANY_LIST")
    for indcat in ["1001000000", "1001001000"]: #電子資訊 ／軟體／半導體相關業 or 軟體及網路相關業
        for emp in range(1,9): #emp 為公司人數選項，從1~8
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            loop.run_until_complete(caller(emp, indcat))  
   
if __name__ == '__main__':
    get_104_crawler()