import sys
import pathlib
import hashlib
from multiprocessing.dummy import Pool
import time
import pandas as pd
sys.path.append(str(pathlib.Path(__file__).parent.parent.resolve()))
sys.path.append(str(pathlib.Path(__file__).parent.parent.parent.resolve()))
from data_collection_system.tools import log
from data_collection_system.db.db_insert import insert_data_list
from text_segmentation import Jieba, Segmentatior, Ckip
from classification import Classifyer
from emotion_detection import EmotionDetection

logger = log.create_logger()
DIR = f"""{str(pathlib.Path(__file__).parent.parent.resolve())}/file/"""
NUM_WORKERS = 8
HTML_TAG_LIST = [
    '<script async','id','class','css',
    'header','table','script','footer',
    'img','src','form','br','p','div',
    'section','main','title','link','href'
]
COLLECTION_NAME = "spam_detection_jieba"

class DataProcesser(object):
    """
    This class is used for data processing

    Args:
        params(dict):
            A dict which has key:
            data_source, target_company_file_dir, search_result_url_dir, search_result_content_dir
        segmentatior(Segmentatior): A Segmentatior
        classifyer(Classifyer): A Classifyer
    Attributes:
        data_source(str): which search engine
        __target_company_list(list)
        keyword(str)
        target_company_file_dir(str): A path of target company file
        search_result_url_dir(str): A path of url of search result
        search_result_content_dir(str): A path of search result content
        segmentatior(Segmentatior)
        classifyer(Classifyer)
    """
    def __init__(self, params: dict, segmentatior: Segmentatior, classifyer: Classifyer):
        if not isinstance(params, dict):
            raise TypeError("Param must be dict")

        if not isinstance(segmentatior, Segmentatior):
            raise TypeError("Param must be dict")

        if not isinstance(classifyer, Classifyer):
            raise TypeError("Param must be dict")

        self.data_source = params["data_source"]
        self.__target_company_list = []
        self.keyword = ""
        self.target_company_file_dir = params['target_company_file_dir']
        self.search_result_url_dir = params['search_result_url_dir']
        self.search_result_content_dir = params['search_result_content_dir']
        self.segmentatior = segmentatior
        self.classifyer = classifyer
        
    def __two_dimension_list_to_one(self, data: list) -> list:
        """Convert 2D list to 1D list
        
        Args:
            data(2D list)
        Returns:
            1D list
        Raises:
            TypeError: An error caused by wrong type of input params
        """
        if not isinstance(data, list):
            raise TypeError("Param must be list")
        return [j for sub in data for j in sub]
    
    def __extract_html_features(self, web_content: str, keyword: str) -> dict:
        """Extract the features from HTML structure
        
        Args:
            web_content(str): A HTML of web content in string format
            keyword(str): A target search keyword
        Returns:
            features(dict): A dict of features composed by HTML_TAG_LIST
        Raises:
            TypeError: An error caused by wrong type of input params
        """
        if not (isinstance(web_content, str) and isinstance(keyword, str)):
            raise TypeError("Params must be str")
        features = {}
        for tag in HTML_TAG_LIST:
            features[tag] = web_content.count(tag)
        features[tag] = web_content.count(keyword)
        return features 
    
    def __get_web_content(self, filename: str) -> str:
        """Read the HTML file in str format
        
        Args:
            filename(str)
        Returns:
            str: file content or empty string
        Raises:
            OSError: An error occurs when reading file
        """
        try:
            with open(filename, 'r', encoding="utf-8") as file:
                return file.read()
        except OSError as error:
            logger.error(f"__get_web_content of {filename} with {error}")
            return ""

    def __get_target_company_list_from_txt(self) -> None:
        """Read the target company list from txt
        Raises:
            OSError: An error occurs when reading file
        """
        try:
            with open(self.target_company_file_dir, 'r', encoding="utf-8") as file:
                self.__target_company_list = [line.replace('\n','') for line in file]
        except OSError as error:
            log_msg = (
                f"__get_target_company_list_from_txt of"
                f" {self.__target_company_list} with {error}"
            )
            logger.error(log_msg)
            raise error
            
    def __get_url_list_by_company_name(self, company: str) -> None:
        """Read the url list by company name from txt
        
        Args:
            company(str)
        Returns:
            url_list(list): A search result url list of company
        Raises:
            OSError: An error occurs when reading file
        """

        try:
            file_name = f"{self.search_result_url_dir}{company}_url_list.txt"
            with open(file_name, 'r', encoding="utf-8") as file:
                url_list = []
                for line in file:
                    if line != '\n':
                        url_list.append(line.replace('\n',''))
                        
                return url_list

        except OSError as error:
            logger.error(f"""get_url_list_by_company_name {company} with {error}""")
            raise error

    def processing(self) -> None:
        """
        Do data processing using multi-processing
        1. Get the target company list from txt
        2. Get features of each url using multi-processing(call caller function)
        3. Convert features(2D list) to 1D list
        4. Write into excel
        5. Insert to DB
        6. Release segmentatior model
        """
        self.__get_target_company_list_from_txt()

        if isinstance(self.segmentatior, Jieba):
            self.segmentatior.add_word(self.__target_company_list)

        with Pool(NUM_WORKERS) as pool:
            features_list = pool.map(self.__caller, self.__target_company_list)

        features_list = self.__two_dimension_list_to_one(features_list)
        pd.DataFrame(features_list).to_excel(
            f"{DIR}testing_jieba.xlsx", index=False, encoding='utf-8-sig'
        )
        insert_data_list(features_list, COLLECTION_NAME) 
        if isinstance(self.segmentatior, Ckip):
            self.segmentatior.delete_model()
        
    def __caller(self, company: str) -> list:
        """Process each url of each company
        1. Read the web content(HTML) from txt
        2. Extract HTML structure features
        3. Extract features of part of speech
        Args:
            company(str)
        Returns:
            features_list(list)
        """
        logger.info(f"__caller {company}")
        if not company:
            return []

        url_list = self.__get_url_list_by_company_name(company)
        features_list = []
        for url in url_list:
            logger.info(url)
            filename = (
                f"{self.search_result_content_dir}{company}"
                f"/{hashlib.md5(url.encode('utf-8')).hexdigest()}.txt"
            )
            web_content = self.__get_web_content(filename)
            if not web_content:
                continue

            features_html = self.__extract_html_features(web_content, company)
            if not features_html:
                continue
                
            features_html['company'] = company
            features_html['url'] = url
            features_html['label'] = self.classifyer.classify_url(url)
            features_html['label2'] = self.classifyer.classify_web_page_content(
                                                          url, web_content, "面試心得"
                                                      )
            features_text = self.segmentatior.get_stat_of_part_of_speech_by_web_content(web_content)
            features_text.update(features_html)
            features_list.append(features_text)
            
        return features_list

if __name__ == '__main__':
    start_time = time.time()
    DATA_SOURCE = "google"
    params = {
       "data_source" : "google",
       "target_company_file_dir" : f"""{DIR}company_list.txt""",
       "search_result_url_dir" : f"""{DIR}search_result/{DATA_SOURCE}_search_url_result/""",
       "search_result_content_dir" :f"""{DIR}search_result/{DATA_SOURCE}_search_content_result/""",
    }
    emtion_detector = EmotionDetection(f"{DIR}chinese_emotional_dictionary.xlsx")
    emtion_detector.get_sentment_dict()
    processer = DataProcesser(
        params, 
        Jieba(emtion_detector), 
        Classifyer(f"{DIR}blocklist/non_block.xlsx")
    )
    processer.processing()
    logger.info(f"The time consuming of data processing is : {time.time() - start_time}")