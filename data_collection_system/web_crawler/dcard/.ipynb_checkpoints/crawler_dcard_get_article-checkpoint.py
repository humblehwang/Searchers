import sys
import pathlib
import re
import requests
import jieba
from bs4 import BeautifulSoup
import matplotlib.pyplot as plt
from wordcloud import WordCloud
from aiohttp import ClientSession
from bs4 import BeautifulSoup
import asyncio
import time
from utils import convert_month, padding, get_list_from_txt, process_datetime
import hashlib 
import db_insert, db_query
import log
import json
import cloudscraper

logger = log.create_logger()
DIR = f"""{str(pathlib.Path(__file__).parent.resolve())}/file/"""
TARGET_URL = 'https://www.dcard.tw/service/api/v2/'
WAIT_TIME = 5
WAIT_TIME_2 = 30

async def caller(article_id_list):
    tasks = [asyncio.create_task(crawl_article(article_id)) for article_id in article_id_list]  # 建立任務清單
    results = await asyncio.gather(*tasks)  #打包任務清單及執行
        
async def crawl_article(article_id):
    try:
        if article_id == '':
            return
        
        target_url = f"""{TARGET_URL}posts/{article_id}"""
        scraper = cloudscraper.create_scraper()
        response = scraper.get(target_url)
        if response.status_code == 200:
            response_data = json.loads(response.text)
            data = {
                "author": "",
                "board": response_data['forumAlias'],
                "title": response_data['title'],
                "date_time": response_data['createdAt'].replace('-','/').replace('T',' ')[:19],
                "source": "DCARD",
                "num_comment":response_data['commentCount'],
                "url":target_url,
                "article_id":article_id,
                "content":response_data['content']
            }
            logger.info(data['title'])
            db_insert.insert_data(data, "article")
            time.sleep(WAIT_TIME)
        else:
            logger.error(f"""{target_url} with {response.status_code}""")
            time.sleep(WAIT_TIME_2)
            
    except asyncio.TimeoutError:
        logger.error(f"""{target_url} with timeout""")
        time.sleep(WAIT_TIME_2)
        
    except Exception as error:
        logger.error(f"""{target_url} with {str(error)}""")
        time.sleep(WAIT_TIME_2)

def get_article(target_board):
    start_time = time.time() 
    existed_article_id_list = db_query.get_existed_article_id("DCARD", target_board)
    article_id_list = list(set(get_list_from_txt(f"""{DIR}dcard_{target_board}_url_list.txt""")).difference(set(existed_article_id_list)))
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(caller(article_id_list))  #執行協程(coroutine)
    logger.info(f"""Time consuming of get_article : {str(time.time() - start_time)}""")

