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
            #把最新index到index 0的頁面全部加入帶爬蟲的page_list，如果遇到某個頁面的文章url已經儲存在DB，就停止
            for index in range(int(latest_index) + 1, 0, -1): 
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

async def caller(url_list):
    async with ClientSession() as session:
        tasks = [asyncio.create_task(crawl_article(url, session)) for url in url_list]  # 建立任務清單
        results = await asyncio.gather(*tasks)  # 打包任務清單及執行

async def crawl_article(url, session):
    try:
        async with session.get(url) as response:  #非同步發送請求
            html_body = await response.text()
            soup = BeautifulSoup(html_body, 'lxml')
            
            if len(soup.find_all('span', class_ = 'article-meta-value')) == 4:
                author = soup.find_all('span', class_ = 'article-meta-value')[0].getText()
                board = url[url.find("bbs/") + 4:url.find("bbs/") + 4 + url[url.find("bbs/") + 4:].find('/')]
                title = soup.find_all('span', class_ = 'article-meta-value')[2].getText()
                tmp = soup.find_all('span', class_ = 'article-meta-value')[3].getText()
                tmp = tmp.split(' ')
                date_time = process_datetime(tmp)

            elif len(soup.find_all('span', class_ = 'article-meta-value')) == 3: #回復文章的文章沒有board，所以從url擷取
                
                board = url[url.find("bbs/") + 4:url.find("bbs/") + 4 + url[url.find("bbs/") + 4:].find('/')]

                tmp = soup.find_all('span', class_ = 'article-meta-value')[2].getText()
                tmp = tmp.split(' ')
                
                if len(tmp) == 5: #index 2是datetime
                    date_time = process_datetime(tmp)
                    author = soup.find_all('span', class_ = 'article-meta-value')[0].getText()
                    title = soup.find_all('span', class_ = 'article-meta-value')[1].getText()
                else:
                    author = soup.find_all('span', class_ = 'article-meta-value')[0].getText()
                    title = soup.find_all('span', class_ = 'article-meta-value')[1].getText()
                    board = url[url.find("bbs/") + 4:url.find("bbs/") + 4 + url[url.find("bbs/") + 4:].find('/')]
                    date_time = ''
            else:
                board = url[url.find("bbs/") + 4:url.find("bbs/") + 4 + url[url.find("bbs/") + 4:].find('/')]
                author = ''
                title = ''
                date_time = ''


            #find content
            main_container = soup.find(id='main-container')
            all_text = main_container.text
            pre_text = all_text.split('--')[0]
            texts = pre_text.split('\n')
            contents = texts[2:]
            content = '\n'.join(contents)
            
            if date_time == '': #若標頭沒有時間資訊，或許可以從內文查到。ex:https://www.ptt.cc/bbs/Tech_Job/M.1496455868.A.304.html
                if '時間' in content.split('\n')[0]:
                    tmp = content.split('\n')[0][content.split('\n')[0].find('時間:') + 3:]
                    tmp = tmp.split(' ')
                    date_time = process_datetime(tmp)
                
            num_comment = len(soup.find_all('span', 'f3 push-content'))
            
            data = {
                "author": author,
                "board": board,
                "title": title,
                "date_time": date_time,
                "source": "PTT",
                "num_comment":num_comment,
                "url":url,
                "article_id":hashlib.md5(url.encode('utf-8')).hexdigest(),
                "content":content
            }
            db_insert.insert_data(data, "article")
            
            #處理留言
            user_list = soup.find_all('span', 'f3 hl push-userid')
            tag_list = soup.find_all('span', 'push-tag')
            content_list = soup.find_all('span', 'f3 push-content')

            comment_list = []
            for index in range(len(content_list)):
                comment = {
                    "user" : user_list[index].getText().replace(' ', '').replace(':', '').strip(),
                    "tag" : tag_list[index].getText().replace(' ', '').replace(':', '').strip(),
                    "content" : content_list[index].getText().replace(' ', '').replace(':', '').strip(),
                    "url" : url,                         
                    "article_id" : hashlib.md5(url.encode('utf-8')).hexdigest(),
                    "comment_id" : hashlib.md5(content_list[index].getText().replace(' ', '').replace(':', '').strip().encode('utf-8')).hexdigest(),

                }

                comment_list.append(comment)
            if comment_list:
                db_insert.insert_data_list(comment_list, "comment")
            
    except asyncio.TimeoutError:
        logger.error(f"""{url} with timeout""")
        time.sleep(30)
        
    except Exception as error:
        logger.error(f"""{url} with {str(error)}""")

def get_article(target_board):
    target_url = f'''https://www.ptt.cc/bbs/{target_board}/index.html'''
    start_time = time.time()  #開始執行時間
    existed_url_list = db_query.get_existed_url("PTT", target_board)
    url_list = list(set(get_list_from_txt(f"""{DIR}ptt_{target_board}_url_list.txt""")).difference(set(existed_url_list)))
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(caller(url_list))  #執行協程(coroutine)
    logger.info(f"""Time consuming of get_article : {str(time.time() - start_time)}""")

    