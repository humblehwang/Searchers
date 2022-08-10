import sys
import pathlib
import abc
import os
import hashlib
sys.path.append(str(pathlib.Path(__file__).parent.parent.resolve()))
sys.path.append(str(pathlib.Path(__file__).parent.parent.parent.resolve()))
from data_collection_system.tools import log

logger = log.create_logger()

"""
get_target_company_list_from_txt -> 
    search ->  
        (multiprocessing)
        do_search -> get_search_url ->
        1. save_url_list_to_txt
        2. caller -> get_web_content -> save_web_content_to_txt
"""
class SearchEngine(abc.ABC):
    """
    This class is a interface of search engine

    Attributes:
        query_target(str): search keyword
        max_search_page(int)
        pause_time(int): The time interval between doing search
        target_company_file_dir(str): The path of the company to be searched
        search_result_url_dir(str): The path where store the urls of search result
        search_result_content_dir(str): The path where store the contents of search result
    """
    def __init__(self):
        #self.__class__.__name__
        self.query_target = ""
        self.max_search_page = 0
        self.pause_time = 0
        self.target_company_file_dir = ""
        self.search_result_url_dir = ""
        self.search_result_content_dir = ""
        
    def get_target_company_list_from_txt(self) -> None: 
        """Get the company list to be searched

        Returns:
            column: 0
            sharing: 1
            not-consider: 2

        Raises:
            OSError: An error caused by reading txt
        """
        try:
            with open(self.target_company_file_dir, 'r', encoding="utf-8") as f:
                return [line.replace('\n','') for line in f]
        except OSError as error:
            logger.error(f"""get_target_company_list_from_txt with {error}""")
            raise error

    def save_web_content_to_txt(self, web_content: str, url: str, company_name: str) -> None:
        """Save web content(HTML) to txt
        
        Args:
            web_content(str): A HTML of web content in string format
            company_name(str)
        Raises:
            OSError: An error caused by writing txt
        """

        try:
            if not os.path.exists(f"""{self.search_result_content_dir}"""):
                os.makedirs(f"""{self.search_result_content_dir}""")
                
            if not os.path.exists(f"""{self.search_result_content_dir}{company_name}"""):
                os.makedirs(f"""{self.search_result_content_dir}{company_name}""")                
            file_name = (
                f"{self.search_result_content_dir}{company_name}"
                f"/{hashlib.md5(url.encode('utf-8')).hexdigest()}.txt"
            )
            with open(file_name, 'w', encoding="utf-8") as file:
                file.write(web_content)

        except OSError as error:
            logger.error(f"""save_web_content_to_txt with {error}""")
            raise error

    def save_url_list_to_txt(self, company_name: str, url_list: list) -> None:
        """Save url list to txt
        
        Args:
            company_name(str)
            url_list(list): The url list of search result   
        Raises:
            OSError: An error caused by writing txt
        """
        try:
            #if not exist then creat the file
            if not os.path.exists(f"""{self.search_result_url_dir}"""):
                os.makedirs(f"""{self.search_result_url_dir}""")

            file_name = (
                f"{self.search_result_url_dir}{company_name}_url_list.txt"
            )
            with open(file_name, 'w', encoding="utf-8") as file:
                for url in url_list:
                    file.write("%s\n" % url)

        except OSError as error:
            logger.error(f"save_url_list_to_txt with {error}")
            raise error


    def search(self):
        """search entry point"""
    
    def do_search(self):
        """get url list and get each web content"""

    
    def get_search_url(self, keyword):
        """get the search result url list"""
    
    def caller(self):
        """get web content using asyncio"""
    
    def get_web_content(self):
        """get web content"""
