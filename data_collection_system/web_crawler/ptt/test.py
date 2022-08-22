"""
utility : get 要爬文章的url
"""
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

logger = log.create_logger()

DIR = f"""{str(pathlib.Path(__file__).parent.resolve())}/file/"""
month_set = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec']

class pttUrlGetter():
    def __init__(self, url, latest_url, is_first, target_board):
        self.url = url
        self.url_list = []
        self.page_list = []
        self.title_list = []
        self.existed_latest_url = latest_url
        self.is_first = is_first
        self.target_board = target_board
        
    def get_previous_pages(self):    
        r = requests.get(self.url)
        soup = BeautifulSoup(r.text, "html.parser")
        # 抓取按鈕群
        btn = soup.select('div.btn-group > a')
        # 抓取上一頁按鈕的網址
        up_page_href = btn[3]['href']
        # 在網址後加上上一頁的網址
        next_page_url = 'https://www.ptt.cc' + up_page_href
        #得到最新頁面的index
        latest_index = next_page_url[next_page_url.find("index")+5:next_page_url.find(".html")]
        
        if not self.is_first:
            for index in range(int(latest_index) + 1, 0, -1): #把最新index到index 0的頁面全部加入帶爬蟲的page_list，如果遇到某個頁面的文章url已經儲存在DB，就停止
                next_page_url = f"""{self.url[:self.url.find("index")+5]}{index}.html"""
                self.page_list.append(next_page_url)
                if not self.get_all_href(next_page_url):
                    break
                
        #第一次爬某個板要換成下列三行，利用非同步的方式去get所有文章的url        
        else:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            loop.run_until_complete(self.caller(latest_index))  
   
    async def caller(self, latest_index):
        async with ClientSession() as session:
            tasks = [asyncio.create_task(self.get_all_href_async( f"""{self.url[:self.url.find("index")+5]}{index}.html""", session)) for index in range(int(latest_index) + 1, 0, -1)]  # 建立任務清單
            await asyncio.gather(*tasks)  # 打包任務清單及執行

    # 抓取標題網址
    def get_all_href(self, target_url):
        r = requests.get(target_url)
        soup = BeautifulSoup(r.text, "html.parser")
        # 抓取文章標題
        results = soup.select("div.title")
        # 尋訪每個標題 取得網址
        for item in results[::-1]:
            a_item = item.select_one("a")
            if a_item:
                #所要儲存的網站網址
                url = 'https://www.ptt.cc' + a_item.get('href')

                if url == target_url or url == self.existed_latest_url: #如果已經到了最新的文章url，就不需要在往下查url
                    return False

                # 儲存網址至佇列
                self.url_list.append(url)
        return True
        
    # 抓取標題網址
    async def get_all_href_async(self, target_url, session):
        async with session.get(target_url) as response:
            html_body = await response.text()
            soup = BeautifulSoup(html_body, "html.parser")
            # 抓取文章標題
            results = soup.select("div.title")
            # 尋訪每個標題 取得網址
            for item in results:
                a_item = item.select_one("a")
                if a_item:
                    #所要儲存的網站網址
                    url = 'https://www.ptt.cc' + a_item.get('href')

                    if url == self.target_url or url == self.existed_latest_url: #如果已經到了最新的文章url，就不需要在往下查url
                        break
                    # 儲存網址至佇列
                    self.url_list.append(url)
    
    def save_url_list_to_txt(self):
        with open(f"""{DIR}ptt_{self.target_board}_url_list.txt""", 'w') as fp:
            for url in self.url_list:
                fp.write("%s\n" % url)
                


def get_url_list(target_board, is_first): 
    target_url = f'''https://www.ptt.cc/bbs/{target_board}/index.html'''
    
    start_time = time.time()  #開始執行時間
    latest_url = db_query.get_latest_existed_url("PTT",target_board) #DB裡面最新文章的url
    ptt = crawlerPtt(target_url, latest_url, is_first, target_board)
    ptt.get_previous_pages()
    
    existed_url_list = db_query.get_existed_url("PTT",target_board)
    ptt.url_list = list(set(ptt.url_list).difference(set(existed_url_list)))

    ptt.save_url_list_to_txt()
    
    logger.info(f"""花費: {str(time.time() - start_time)}""")



"""
utility : 跟DB insert、update相關的function
"""
from bson.objectid import ObjectId
import pymongo
import pandas as pd
import log
import utils
from utils import get_db_connection


logger = log.create_logger()
    
def get_existed_url(source, board):
    #utility: get existed url list (in DB)
    try:
        db = get_db_connection()
        db.list_collection_names()
        collection = db['article']
        query = {
            "source" : source,
            "board" : board,
        }
        data = list(collection.find(query))
        url_list = []
        for d in data:
            url_list.append(d['url'])
        return url_list
    except Exception as error:
        logger.error(f"""get_existed_url with {error}""")
        return False
    
def get_latest_existed_url(source, board):
    """
    utility: get latest existed url list (in DB) and if the latest datetime of data is not correct datetime format, we will delete it and query again
    """
    try:
        db = get_db_connection()
        db.list_collection_names()
        collection = db['article']
        query = {
            "source" : source,
            "board" : board,
        }
        while 1 :
            data = list(collection.find(query).sort([("date_time",-1)]).limit(-1))[0]
            if not data: 
                return ''
        
            if utils.check_time_format(data['date_time']):
                break
                
            collection.delete_one({"_id":ObjectId(data['_id'])})
        return data['url']
    
    except Exception as error:
        logger.error(f"""get_latest_existed_url with {error}""")
        return False
    
def get_existed_article_id(source, board):
    #utility: get existed url list (in DB)
    try:
        db = get_db_connection()
        db.list_collection_names()
        collection = db['article']
        query = {
            "source" : source,
            "board" : board,
        }
        data = list(collection.find(query))
        url_list = []
        for d in data:
            url_list.append(d['article_id'])
        return url_list
    except Exception as error:
        logger.error(f"""get_existed_article_id with {error}""")
        return False
    
def get_latest_existed_article_id(source, board):
    """
    utility: get latest existed url list (in DB) and if the latest datetime of data is not correct datetime format, we will delete it and query again
    """
    try:
        db = get_db_connection()
        db.list_collection_names()
        collection = db['article']
        query = {
            "source" : source,
            "board" : board,
        }
        while 1 :
            data = list(collection.find(query).sort([("date_time",-1)]).limit(-1))[0]
            if not data: 
                return ''
        
            if utils.check_time_format(data['date_time']):
                break
                
            collection.delete_one({"_id":ObjectId(data['_id'])})
        return data['article_id']
    
    except Exception as error:
        logger.error(f"""get_latest_existed_article_id with {error}""")
        return False
    