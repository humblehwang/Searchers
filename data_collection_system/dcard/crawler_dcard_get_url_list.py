import sys
import pathlib
import requests
import time
import json
import log
import db_query
import cloudscraper

logger = log.create_logger()
TARGET_URL = 'https://www.dcard.tw/service/api/v2/'
DIR = f"""{str(pathlib.Path(__file__).parent.resolve())}/file/"""

WAIT_TIME = 5
WAIT_TIME_2 = 30

def save_url_list_to_txt(url_list, target_board):
    with open(f"""{DIR}dcard_{target_board}_url_list.txt""", 'w') as fp:
        for url in url_list:
            logger.info(url)
            fp.write("%s\n" % url)
            
def get_url_list(is_first, target_board, last_article_id):
    article_id_list = []
    scraper = cloudscraper.create_scraper()

    if is_first:
        r =  scraper.get(f"""{TARGET_URL}forums/{target_board}/posts?limit=100""")
        article_id_list = [d['id'] for d in json.loads(r.text)]
        last_article_id = article_id_list[-1]
        
        while True:
            r = scraper.get(f"""{TARGET_URL}forums/{target_board}/posts?limit=100&before={last_article_id}""") #每次都查找最後得到ID的前100篇文章
            if r.status_code == 200:
                if r.text == '[]': #已經爬到第一篇文章了
                    break
                    
                data = json.loads(r.text)
                logger.info(data[-1]['id'])
                if data[-1]['id'] == last_article_id:
                    break

                article_id_list += [d['id'] for d in data]
                last_article_id = article_id_list[-1]
                time.sleep(WAIT_TIME)

            else:
                logger.error(f"""{TARGET_URL}forums/{target_board}/posts?limit=100&before={last_article_id} with {r.status_code}""")
                time.sleep(WAIT_TIME_2)
    else:
        while True:
            r = scraper.get(f"""{TARGET_URL}forums/{target_board}/posts?limit=100&after={last_article_id}""") #每次都查找最後得到ID的前100篇文章
            logger.warn(r.status_code)
            if r.status_code == 200:
                
                if r.text == '[]': #已經爬到第一篇文章了
                    break
                    
                data = json.loads(r.text)

                article_id_list += [d['id'] for d in data]
               
                if len(data) != 100: #call一次就可以得到最新文章ID list
                    break
                
                time.sleep(WAIT_TIME)

            else:
                logger.error(f"""{TARGET_URL}forums/{target_board}/posts?limit=100&after={last_article_id} with {r.status_code}""")
                #time.sleep(WAIT_TIME_2)
                break
    
    save_url_list_to_txt(article_id_list, target_board)

def get_dcard_url_list(target_board, is_first): 
    start_time = time.time()  #開始執行時間
    latest_article_id = "239270427"#db_query.get_latest_existed_article_id("DCARD",target_board) #DB裡面最新文章的url
    get_url_list(is_first, target_board, latest_article_id)

    logger.info(f"""花費: {str(time.time() - start_time)}""")

   