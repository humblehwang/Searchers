import sys
import pathlib
sys.path.append(str(pathlib.Path(__file__).parent.parent.resolve()))
sys.path.append(str(pathlib.Path(__file__).parent.parent.parent.resolve()))
import abc
from data_collection_system.tools import log
from data_collection_system.tools.exception  import ReadTxtError, WriteTxtError
import os
import hashlib 

logger = log.create_logger()

"""
get_target_company_list_from_txt -> 
    search ->  
        (multiprocessing)
        do_search -> get_search_url ->
        1. save_url_list_to_txt
        2. caller -> get_web_content -> save_web_content_to_txt
"""
class searchEngine(abc.ABC):
    def __init__(self):
        #self.__class__.__name__
        self.query_target = ""
        self.max_search_page = 0
        self.pause_time = 0
        self.target_company_file_dir = ""
        self.search_result_url_dir = ""
        self.search_result_content_dir = ""
        
    def get_target_company_list_from_txt(self):   
        try:
            with open(self.target_company_file_dir) as f:
                return [line for line in f]
        except Exception as error:
            raise ReadTxtError(f"""get_target_company_list_from_txt with {error}""")

    def save_web_content_to_txt(self, web_content, url, company_name):
        try:
            if not os.path.exists(f"""{self.search_result_content_dir}"""):
                os.makedirs(f"""{self.search_result_content_dir}""")
                
            if not os.path.exists(f"""{self.search_result_content_dir}{company_name}"""):
                os.makedirs(f"""{self.search_result_content_dir}{company_name}""")                

            with open(f"""{self.search_result_content_dir}{company_name}/{hashlib.md5(url.encode('utf-8')).hexdigest()}.txt""", 'w') as fp:
                fp.write(web_content)
        except Exception as error:
            raise WriteTxtError(f"""save_web_content_to_txt with {error}""")

    def save_url_list_to_txt(self, company_name, url_list):
        try:
            #if not exist then creat the file
            if not os.path.exists(f"""{self.search_result_url_dir}"""):
                os.makedirs(f"""{self.search_result_url_dir}""")

            with open(f"""{self.search_result_url_dir}{company_name}_url_list.txt""", 'w') as fp:
                for url in url_list:
                    fp.write("%s\n" % url)
        except Exception as error:
            raise WriteTxtError(f"""save_url_list_to_txt with {error}""")

    def search(self):
        pass
    
    def do_search(self):
        pass
    
    def get_search_url(self, keyword):
        pass
    
    def caller(self):
        pass
    
    def get_web_content(self):
        pass