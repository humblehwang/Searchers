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

