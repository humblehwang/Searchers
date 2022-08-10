import pathlib
import sys
from urllib.parse import urlparse
import pandas as pd
sys.path.append(str(pathlib.Path(__file__).parent.parent.resolve()))
sys.path.append(str(pathlib.Path(__file__).parent.parent.parent.resolve()))
from data_collection_system.tools.url_block import get_block_url_set, get_non_block_url_set 


class Classifyer(object):
    """
    This class is used to label the input url and web content
    
    Args:
        non_block_filename(str): The file path of non-block rule

    Attributes:
        __non_block_filename(str)
        __domain_table(dict)
        __block_url_set(set)
        __non_block_url_set(set)

    """

    def __init__(self, non_block_filename: str) -> None :
        if not isinstance(non_block_filename, str):
            raise TypeError("Param must be str")

        self.__non_block_filename = non_block_filename
        self.__domain_table = self.__get_domain_table()
        self.__block_url_set = get_block_url_set()
        self.__non_block_url_set = get_non_block_url_set()

    def __get_domain_table(self) -> dict:
        """Get the label rules(column, sharing and not-consider) of url from the definition.

        Returns:
            domain_table (dict)

        Raises:
            KeyError: An error occured accessing the colum of dataframe
        """

        df_non_block = pd.read_excel(self.__non_block_filename)
        if 'type' not in df_non_block.columns or 'domain' not in df_non_block.columns:
            raise KeyError("type or domain not in dataframe column")

        domain_table = {}
        for row in df_non_block.iloc:
            domain_table[row['domain']] = row['type']
        return domain_table
    
    def classify_web_page_content(self, url: str, web_content: str, keyword: str) -> int:
        """Get the label(column, sharing and not-consider) of url from __domain_table
        
        Args:
            url(str): An url wanting to be labeled
            web_content(str): A web content correposding to the url
            keyword(str): A keyword of querying

        Returns:
            column: 0
            sharing: 1
            not-consider: 2

        Raises:
            TypeError: An error caused by wrong type of input params
        """

        if not (isinstance(url, str) and isinstance(web_content, str) and isinstance(keyword, str)):
            raise TypeError("Params must both be str")

        domain = urlparse(url).netloc
        if (domain not in self.__domain_table or 
            self.__domain_table[domain] in ['job', 'pay', 'social_media', 'pixnet.net/blog/']):
            return 2
        elif self.__domain_table[domain] in ['sharing&column', 'column&sharing', 'job&column', 'job&column&sharing']:
            return 1 if web_content.count(keyword) else 0 # if "面試心得" 有在web content，則回傳1 
        elif self.__domain_table[domain] == "column":
            return 0
        elif self.__domain_table[domain] == "sharing":
            return 1
        
    def classify_url(self, url: str) -> int:
        """Get the label(non-block, block, unknown) of url from the url block list.
        
        Args:
            url(str): An url wanting to be labeled
        
        Returns:
            non-block: 0
            block: 1
            unknown: 2
        
        Raises:
            TypeError: An error caused by wrong type of input params
        """

        if not isinstance(url, str):
            raise TypeError("Param must both be str")
        url = url.encode('utf-8')
        for rule in self.__block_url_set:
            if rule in url:
                return 1

        for rule in self.__non_block_url_set:
            if rule in url:
                return 0
        return 2
