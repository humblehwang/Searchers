import sys
import pathlib
sys.path.append(str(pathlib.Path(__file__).parent.parent.resolve()))
sys.path.append(str(pathlib.Path(__file__).parent.parent.parent.resolve()))
import pandas as pd
import re
from ckiptagger import data_utils, construct_dictionary, WS, POS, NER
import os
from data_collection_system.tools.exception import LoadModelError
from collections import Counter 
import abc

class Segmentatior(abc.ABC):
    
    def __init__(self):
        self.text_columns = 
        self.model_dir = ""
        
    def delete_model(self):
        pass
        
    def load_model(self):
        pass
    
    @staticmethod
    def chinese_word_filter(string):
        if not isinstance(string):
            raise ValueError("Arguments must both be str")
            
        return "".join(re.findall(r'[\u4e00-\u9fff]+', string))
    
    def get_most_common_dict(self, counter, threshold = 10):
        result = {}
        most_common_list = counter.most_common()
        for i in range(threshold):
            result[f"most common number {i + 1}"] = most_common_list[i][0] if i < len(counter) else "None"
        return result

    def get_stat_counter(self, counter):
        result = Counter()
        for column in self.text_columns:
            result[column] = counter[column] if column in counter else 0
        return result
    
    def get_stat_of_part_of_speech_by_web_content(self, web_content):
        pass
    
    
class Ckip(Segmentatior):
    
    def __init__(self):
        super().__init__()
        self.text_columns = ["A","Caa","Cab","Cba","Cbb","D","Da","Dfa","Dfb","Di","Dk","DM","I","Na","Nb","Nc","Ncd","Nd","Nep","Neq","Neq","Nes","Neu","Nf","Ng","Nh","Nv","P","T","VA","VAC","VB","VC","VCL","VD","VF","VE","VG","VH","VHC","VI","VJ","VK","VL","V_2","DE","SHI","FW"]
        self.model_dir = f"{str(pathlib.Path(__file__).parent.parent.resolve())}/file/text_segmentation/data"
        self.ws = ""
        self.pos = ""
        self.ner = ""
        self.load_model()
        
    def delete_model(self):
        del self.ws 
        del self.pos
        del self.ner  
        
    def load_model(self):
        if not os.path.exists(self.model_dir):
            raise LoadModelError("The model of ckiptagger doesn't exist")
            
        self.ws = WS(self.model_dir)
        self.pos = POS(self.model_dir)
        self.ner = NER(self.model_dir)
        
    def __combine_word_pos_sentence(self, word_sentence, pos_sentence):
        assert len(word_sentence) == len(pos_sentence)
        return [{word:pos} for word, pos in zip(word_sentence, pos_sentence)]
                       
    def __get_pos_and_word_sentence(self, web_content):
        word_sentence_list = self.ws([web_content])
        pos_sentence, word_sentence = self.pos(word_sentence_list)[0], word_sentence_list[0]
        return word_sentence, pos_sentence
       
    def __get_most_common_dict(self, counter):
        threshold = 10
        result = {}
        most_common_list = counter.most_common()
        for i in range(threshold):
            result[f"most common number {i + 1}"] = most_common_list[i][0] if i < len(counter) else "None"
        return result
    
    def __get_stat_counter(self, counter):
        result = Counter()
        for column in self.text_columns:
            result[column] = counter[column] if column in counter else 0
        return result

    def get_stat_of_part_of_speech_by_web_content(self, web_content):
        if not web_content:
            return pd.DataFrame()
        
        string = self.__chinese_word_filter(web_content)    
        word_sentence, pos_sentence = self.__get_pos_and_word_sentence(string)  
        counter = self.__get_stat_counter(Counter(pos_sentence))
        most_common = self.__get_most_common_dict(counter)
        self.merge_dicts(most_common, dict(counter))
        return most_common
            
