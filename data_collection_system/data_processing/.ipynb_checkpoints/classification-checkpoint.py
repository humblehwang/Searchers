import sys
import pathlib
sys.path.append(str(pathlib.Path(__file__).parent.parent.resolve()))
sys.path.append(str(pathlib.Path(__file__).parent.parent.parent.resolve()))
from data_collection_system.tools.url_block import get_block_url_set, get_non_block_url_set 
import pandas as pd

class Classifyer():
    
    def __init__(self, non_block_filename: str):
        if not isinstance(non_block_filename, str):
            raise ValueError("Arguments must both be str")
        
        self.__non_block_filename = non_block_filename
        self.__domain_table = self.__get_domain_table()
        self.__block_url_set = get_block_url_set()
        self.__non_block_url_set = get_non_block_url_set()
        
    def __get_domain_table(self) -> dict:
        """Get the label(column, sharing and not-consider) of url from the definition.
        
        Args:
            url : An url wanting to be labeled
            web_content : A web content correposding to the url
        Returns:
            domain_table
            
        """
        
        df = pd.read_excel(self.__non_block_filename)

        domain_table = {}
        for d in df.iloc:
            domain_table[d['domain']] = d['type']
        return domain_table
    
    def classify_web_page_content(self, url: str, web_content: str, keyword: str) -> int:
        """Get the label(column, sharing and not-consider) of url from the definition.
        
        Args:
            url : An url wanting to be labeled
            web_content : A web content correposding to the url
            keyword: A keyword of querying
        Returns:
            column: 0,
            sharing: 1,
            not-consider: 2
            
        """
        if not (isinstance(url, str) and isinstance(web_content, str) and isinstance(keyword, str)):
            raise ValueError("Arguments must both be str")
            
        if url not in self.__domain_table or self.__domain_table[url] in ['job', 'pay', 'social_media', 'pixnet.net/blog/']:
            return 2
        
        elif self.__domain_table[url] in ['column&sharing', 'job&column', 'job&column&sharing']:
            return web_content.count(keyword) 
        
        elif self.__domain_table[url] == "column":
            return 0
        
        elif self.__domain_table[url] == "sharing":
            return 1
        
    def classify_url(self, url: str) -> int:
        """Get the label(non-block, block, unknown) of url from the block list.
        
        Args:
            url : An url wanting to be labeled
            
        Returns:
            non-block: 0,
            block: 1,
            unknow: 2
            
        """
        if not isinstance(url, str):
            raise ValueError("Url must both be str")
            
        url = url.encode('utf-8')
        for u in self.__block_url_set:
            if u in url:
                return 1
        for u in self.__non_block_url_set:
            if u in url:
                return 0
        return 2

