from typing import List
import helper
from custom_exception import GetWebPageError
from bs4 import BeautifulSoup
import hashlib 
from aiohttp import ClientSession
import asyncio
from model import db_insert

SOURCE = "PTT"

class PTTDataProcesser(object):
    """Get the url list from kafka and do data processing"""
    def __init__(self):
        self.url_list = []
        self.article_list = []
        self.comment_list = []

    def process_articles(self):
        """
        Process articles and comments
        """
        async def caller():
            async with ClientSession() as session:
                tasks = [asyncio.create_task(self.extract_article_data(url, session)) for url in self.url_list]  
                await asyncio.gather(*tasks)

        asyncio.run(caller())
        db_insert.insert_data(self.article_list, "article")
        db_insert.insert_data(self.comment_list, "comment")

    async def extract_article_data(self, url:str, session:ClientSession) -> dict :
        """
        Extract article data from given web_content
        Args:
            url(str)
            session(ClientSession)
        Returns:
            article(dict): A dict of article's information
        """

        def get_article() -> dict:
            if len(soup.find_all('span', class_ = 'article-meta-value')) == 4:
                author = soup.find_all('span', class_ = 'article-meta-value')[0].getText()
                board = url[url.find("bbs/") + 4:url.find("bbs/") + 4 + url[url.find("bbs/") + 4:].find('/')]
                title = soup.find_all('span', class_ = 'article-meta-value')[2].getText()
                tmp = soup.find_all('span', class_ = 'article-meta-value')[3].getText()
                tmp = tmp.split(' ')
                date_time = helper.process_datetime(tmp)

            elif len(soup.find_all('span', class_ = 'article-meta-value')) == 3: 
                # response articles do not have board, so we extract board from url           
                board = url[url.find("bbs/") + 4:url.find("bbs/") + 4 + url[url.find("bbs/") + 4:].find('/')]
                tmp = soup.find_all('span', class_ = 'article-meta-value')[2].getText()
                tmp = tmp.split(' ')
                
                if len(tmp) == 5: #datetime is at index 2
                    date_time = helper.process_datetime(tmp)
                    author = soup.find_all('span', class_ = 'article-meta-value')[0].getText()
                    title = soup.find_all('span', class_ = 'article-meta-value')[1].getText()
                else:
                    author = soup.find_all('span', class_ = 'article-meta-value')[0].getText()
                    title = soup.find_all('span', class_ = 'article-meta-value')[2].getText()
                    board = soup.find_all('span', class_ = 'article-meta-value')[1].getText()
                    #board = url[url.find("bbs/") + 4:url.find("bbs/") + 4 + url[url.find("bbs/") + 4:].find('/')]
                    date_time = ''
                 
            else:
                board = url[url.find("bbs/") + 4:url.find("bbs/") + 4 + url[url.find("bbs/") + 4:].find('/')]
                author = ''
                title = ''
                date_time = ''

            #find article content
            main_container = soup.find(id='main-container')
            all_text = main_container.text
            pre_text = all_text.split('--')[0]
            texts = pre_text.split('\n')
            contents = texts[2:]
            content = '\n'.join(contents)

            # if the header do not have time information, maybe we can find in the article content
            # ex:https://www.ptt.cc/bbs/Tech_Job/M.1496455868.A.304.html
            if date_time == '': 
                if '時間' in content.split('\n')[0]:
                    tmp = content.split('\n')[0][content.split('\n')[0].find('時間:') + 3:]
                    tmp = tmp.split(' ')
                    date_time = helper.process_datetime(tmp)
                
            num_comment = len(soup.find_all('span', 'f3 push-content'))
            
            article = {
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
            return article
        
        def get_commetns() -> List:
            user_list = soup.find_all('span', 'f3 hl push-userid')
            tag_list = soup.find_all('span', 'push-tag')
            content_list = soup.find_all('span', 'f3 push-content')

            comment_list = []
            for index, _ in enumerate(content_list):
                comment = {
                    "user" : user_list[index].getText().replace(' ', '').replace(':', '').strip(),
                    "tag" : tag_list[index].getText().replace(' ', '').replace(':', '').strip(),
                    "content" : content_list[index].getText().replace(' ', '').replace(':', '').strip(),
                    "url" : url,                         
                    "article_id" : hashlib.md5(url.encode('utf-8')).hexdigest(),
                    "comment_id" : hashlib.md5(content_list[index].getText().replace(' ', '').replace(':', '').strip().encode('utf-8')).hexdigest(),
                }

                comment_list.append(comment)
            
            return comment_list

        async with session.get(url) as response:  
            web_content = await response.text()
        
        soup = BeautifulSoup(web_content, 'lxml')
        article = get_article()

        if article:
            self.article_list.append(article)

        comment = get_commetns()
        if comment:
            self.comment_list += comment
        #print(self.url_list,article,comment)





        