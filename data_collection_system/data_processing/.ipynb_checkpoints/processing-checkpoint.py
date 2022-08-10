import sys
import pathlib
sys.path.append(str(pathlib.Path(__file__).parent.parent.resolve()))
sys.path.append(str(pathlib.Path(__file__).parent.parent.parent.resolve()))
import abc
from data_collection_system.tools import log
from data_collection_system.tools.exception import ReadTxtError, WriteTxtError
import os
import hashlib 
from multiprocessing.dummy import Pool
import pandas as pd
import time
import json
from data_collection_system.db.db_insert import insert_data_list
from data_collection_system.data_processing.text_segmentation import Segmentatior
from collections import Counter 
from classification import Classifyer

logger = log.create_logger()
DIR = f"""{str(pathlib.Path(__file__).parent.parent.resolve())}/file/"""
NUM_WORKERS = 10
HTML_TAG_LIST = ['<script async','id','class','css','header','table','script','footer','img','src','form','br','p','div','section','main','title','link','href']
COLLECTION_NAME = "spam_detection"

class DataProcessing():
    
    def __init__(self, params, segmentatior, classifyer):
        self.data_source = params["data_source"]
        self.__target_company_list = []
        self.keyword = ""
        self.target_company_file_dir = params['target_company_file_dir']
        self.search_result_url_dir = params['search_result_url_dir']
        self.search_result_content_dir = params['search_result_content_dir']
        self.segmentatior = segmentatior
        self.classifyer = classifyer
        
    def __insert_data_list_to_db(self, data_list):
        #data_list = json.loads(df.to_json(orient='records'))
        insert_data_list(data_list, COLLECTION_NAME)
        
    def __two_dimension_list_to_one(self, data):
        #2D list to 1D list
        return [j for sub in data for j in sub] 
    
    def __extract_html_features(self, web_content, keyword):
        features = {}
        for tag in HTML_TAG_LIST:
            features[tag] = web_content.count(tag)
        features[tag] = web_content.count(keyword)
        return features  
    
    def __get_web_content(self, filename):
        try:
            with open(filename, 'r') as f:
                return f.read()
            
        except OSError as e:
            return ""
        
        except Exception as error:
            logger.error(f"__get_web_content with {error}")
            
    def __get_target_company_list_from_txt(self):   
        try:
            with open(self.target_company_file_dir) as f:
                 for line in f:
                    self.__target_company_list.append(line.replace('\n',''))
        except Exception as error:
            raise ReadTxtError(f"""get_target_company_list_from_txt with {error}""")
            
    def __get_url_list_by_company_name(self, company):
        try:
            with open(f"{self.search_result_url_dir}{company}_url_list.txt") as f:
                url_list = []
                for line in f:
                    if line != '\n':
                        url_list.append(line.replace('\n',''))
                        
                return url_list
                    
        except Exception as error:
            raise ReadTxtError(f"""get_url_list_by_company_name with {error}""")   
            
    #def __get_label(self, url):
    #    url = url.encode('utf-8')
    #    for site in block_url_set:
    #        if site in url:
    #            return 1
    #    for site in non_block_url_set:
    #        if site in url:
    #            return 0
    #    return 2
    
    def processing(self):
        self.__get_target_company_list_from_txt()
        with Pool(NUM_WORKERS) as pool:
            features_list = pool.map(self.__caller, self.__target_company_list)

        features_list = self.__two_dimension_list_to_one(features_list) 
        pd.DataFrame(features_list).to_excel(f"{DIR}testing.xlsx", index=False, encoding='utf-8-sig')
        self.__insert_data_list_to_db(features_list)   
        self.segmentatior.delete_model()
        
    def __caller(self, company):
        logger.info(company)
        url_list = self.__get_url_list_by_company_name(company)
        features_list = []
        for url in url_list:
            logger.info(url)
            filename = f"{self.search_result_content_dir}{company}/{hashlib.md5(url.encode('utf-8')).hexdigest()}.txt"
            web_content = self.__get_web_content(filename)
            
            if not web_content:
                continue
                
            features_html = self.__extract_html_features(web_content, company) 
            if not features_html:
                continue
                
            features_html['company'] = company
            features_html['url'] = url
            features_html['label'] = self.classifyer.classify_url(url)
            
            features_text = self.segmentatior.get_stat_of_part_of_speech_by_web_content(web_content)
            self.segmentatior.merge_dicts(features_text, features_html)
            features_list.append(features_text)    
            
        return features_list 

if __name__ == '__main__':
    start_time = time.time()
    data_source = "google"
    params = {
       "data_source" : data_source,
       "target_company_file_dir" : f"""{DIR}company_list.txt""",
       "search_result_url_dir" : f"""{DIR}search_result/{data_source}_search_url_result/""",
       "search_result_content_dir" :f"""{DIR}search_result/{data_source}_search_content_result/""",
    }
    processer = DataProcessing(params, Segmentatior(), Classifyer(f"{DIR}blocklist/non_block.xlsx"))
    processer.processing()
    logger.info(f"The time consuming of data processing is : {time.time() - start_time}")