from ast import Pass
import sys
import pathlib
import abc
import re
import os
from typing import Tuple
from collections import Counter
from ckiptagger import WS, POS
import jieba.posseg as pseg
import jieba
sys.path.append(str(pathlib.Path(__file__).parent.parent.resolve()))
sys.path.append(str(pathlib.Path(__file__).parent.parent.parent.resolve()))
from data_collection_system.tools.exception import LoadModelError
from emotion_detection import EmotionDetection


class Segmentatior(abc.ABC):
    """
    This class is a interface of Chinese text segmentation

    Attributes:
        part_of_speech_list(list): A list of part of speech
        model_dir(str): The path of text segmentation model
        emotion_detector(EmotionDetection): Emotion detector
    """
    def __init__(self, emotion_detector: EmotionDetection):
        self.part_of_speech_list = []
        self.model_dir = ""
        self.emotion_detector = emotion_detector

    def chinese_sentence_filter(self, string: str) -> list:
        """Split the text into Chinese sentences

        Args:
            string(str)
        Returns:
            A list of string which only contains Chinese word and punctuation

        Raises:
            TypeError: An error caused by wrong param type
        """
        if not isinstance(string, str):
            raise TypeError("Param must be str")

        string = "".join(re.findall(r'[\u4e00-\u9FA5]+[\uFB00-\uFFFDh]', string))
        return re.split(r"[。|!|！|,|，|?|？]", string)

    def chinese_word_filter(self, string: str) -> str:
        """Filt the Chinese word in given string

        Args:
            string(str)
        Returns:
            A string which only contains Chinese word

        Raises:
            TypeError: An error caused by wrong param type
        """

        if not isinstance(string, str):
            raise TypeError("Param must be str")
            
        return "".join(re.findall(r'[\u4e00-\u9fff]+', string))
    
    def get_most_common_dict(self, counter: Counter, threshold: int=10 ) -> dict:
        """Get the top {threshold} most frequently occurring part of speech 

        Args:
            counter(Counter): The counter of part of speech and its corresponding occuring number
            threshold(int): Default 10, the number of most frequently occuring words be returned
        Returns:
            result(dict): Top {threshold} most frequently occuring part of speech

        Raises:
            TypeError: An error caused by wrong param type
        """
        if not isinstance(counter, Counter):
            raise TypeError("Param must be counter")

        if not isinstance(threshold, int):
            raise TypeError("Param must be int")
        
        result = {}
        most_common_list = counter.most_common()
        for i in range(threshold):
            result[f"most common number {i + 1}"] = most_common_list[i][0] if i < len(counter) else "None"
        return result

    def get_stat_counter(self, counter: Counter) -> Counter:
        """Get the statistical counter part of speech

        Args:
            counter(Counter): The counter of part of speech and its corresponding occuring number
        Returns:
            result(Counter): The counter of part of speech, but the order is sort by part_of_speech_list
            example:
                part_of_speech_list = ['A', 'B', 'C']
                counter = {'A':3, 'B':1}
                result = {'A':3, 'B':1, 'C':0}
        Raises:
            TypeError: An error caused by wrong param type
        """
        if not isinstance(counter, Counter):
            raise TypeError("Param must be counter")

        result = Counter()
        for column in self.part_of_speech_list:
            result[column] = counter[column] if column in counter else 0
        return result



    @abc.abstractmethod
    def get_word_list(self, string: str) -> list:
        """Get the word list"""    
        
    @abc.abstractmethod
    def get_pos_list(self, word_list: list) -> list:
        """Get the part of speech list"""

    @abc.abstractmethod
    def get_stat_of_part_of_speech_by_web_content(self, web_content: str) -> dict:
        """Get statistical counter of part of speech of web content by text segmentation model"""

class Ckip(Segmentatior):
    """
    This class is CKIP text segmentation

    Attributes:
        part_of_speech_list: A list of part of speech
        model_dir(str): The path of text segmentation model
        ws(ckiptagger.api.WS)
        pos(ckiptagger.api.POS)

    """
    def __init__(self, emtion_detector):
        super().__init__(emtion_detector)
        self.part_of_speech_list = [
            "A","Caa","Cab","Cba","Cbb","D","Da","Dfa","Dfb","Di","Dk","DM",
            "I","Na","Nb","Nc","Ncd","Nd","Nep","Neq","Neq","Nes","Neu","Nf",
            "Ng","Nh","Nv","P","T","VA","VAC","VB","VC","VCL","VD","VF",
            "VE","VG","VH","VHC","VI","VJ","VK","VL","V_2","DE","SHI","FW"
        ]
        self.model_dir = f"{str(pathlib.Path(__file__).parent.parent.resolve())}/file/text_segmentation/data"
        self.ws = ""
        self.pos = ""
        self.load_model()
        
    def delete_model(self) -> None:
        """Release the models"""
        del self.ws
        del self.pos
        
    def load_model(self) -> None:
        """Load the text segmentation models

        Raises:
            LoadModelError: An error caused by wrong model path
        """

        if not os.path.exists(self.model_dir):
            raise LoadModelError("The models of ckiptagger doesn't exist")
            
        self.ws = WS(self.model_dir)
        self.pos = POS(self.model_dir)
        
    def combine_word_pos_sentence(self, word_sentence: list, pos_sentence: list) -> list:
        """Combine word list and pos list

        Args:
            word_sentence(list): The words list split by the model
            pos_sentence(list): The part of speech list corresponding word_sentence
        Returns:
            A list: The list which contains words and their part of speech
            example:
                word_sentence = ['心得', '研替', '面試']
                pos_sentence = ['Na', 'VC', 'VC']
                return [{'心得': 'Na'},{'研替': 'VC'},{'面試': 'VC'}]
        Raises:
            TypeError: An error caused by wrong param type
            AssertionError: The size of word_sentence is not equal to the size of pos_sentence
        """
        if not (isinstance(word_sentence, list) and isinstance(pos_sentence, list)):
            raise TypeError("Params must both be list")

        assert len(word_sentence) == len(pos_sentence)
        return [{word:pos} for word, pos in zip(word_sentence, pos_sentence)]

    def get_word_list(self, string: str) -> list:
        """Get pos list using text segmentation models

        Args:
            string(str): A string which only contains Chinese words
        Returns:
            A list of word
            example:
                ['想','請問','內部']
        Raises:
            TypeError: An error caused by wrong param type
        """
        if not isinstance(string, str):
            raise TypeError("Param must be str")

        return self.ws([string])[0]

    def get_pos_list(self, word_list: list) -> list:
        """Get pos list using text segmentation models

        Args:
            word_list(list): A list of word
        Returns:
            pos_sentence(list): A list of part of speech
            example:
                pos_sentence = ['Na', 'VC', 'VC']
        Raises:
            TypeError: An error caused by wrong param type
        """
        if not isinstance(word_list, list):
            raise TypeError("Param must be list")

        pos_sentence = self.pos(word_list)[0]
        return pos_sentence

    def get_stat_of_part_of_speech_by_web_content(self, web_content: str) -> dict:
        """Get statistical counter of part of speech of web content by text segmentation model

        Args:
            web_content(list): A web content(HTML) in string format
        Returns:
            most_common(dict): A dict of stat of part of speech
        Raises:
            TypeError: An error caused by wrong param type
        """
        if not isinstance(web_content, str):
            raise TypeError("Param must be str")

        if not web_content:
            return {}
        sentence_list = self.chinese_sentence_filter(web_content)
        scroe_sentence = self.emotion_detector.get_score_by_sentence_list(sentence_list)
        string = self.chinese_word_filter(web_content)
        word_list = self.get_word_list(string)
        pos_sentence = self.get_pos_list(word_list)
        counter = self.get_stat_counter(Counter(pos_sentence))
        scroe_sentment = self.emotion_detector.get_score_by_sentment(word_list)
        most_common = self.get_most_common_dict(counter)
        most_common.update(dict(counter))
        most_common.update({"scroe_sentment":scroe_sentment,"scroe_sentence":scroe_sentence})
        return most_common


class Jieba(Segmentatior):
    """
    This class is Jieba text segmentation

    Attributes:
        part_of_speech_list: A list of part of speech
    """

    def __init__(self, emtion_detector):
        super().__init__(emtion_detector)
        self.part_of_speech_list = [
            "n","f","s","t","nr","ns","nt","nw",
            "nz","v","vd","vn","a","ad","an",
            "d","m","q","r","p","c","u","xc",
            "w","PER","LOC","ORG","TIME"
        ]
        jieba.enable_parallel(6)

    def get_word_list(self, string: str) -> Tuple[list, list]:
        """Get pos list using text segmentation models

        Args:
            string(str): A string which only contains Chinese words
        Returns:
            A list of word and A list of pos
            example:
                ['想','請問','內部'], ['N','ORG','A']
        Raises:
            TypeError: An error caused by wrong param type
        """
        if not isinstance(string, str):
            raise TypeError("Param must be str")

        word_list, pos_sentence = [], []
        for word, pos in pseg.cut(string):
            word_list.append(word)
            pos_sentence.append(pos)

        return word_list, pos_sentence

    def get_pos_list(self, word_list: list) -> list:
        pass
        """Get pos list using text segmentation models

        Args:
            word_list(list): A list of word
        Returns:
            A list of part of speech
            example:
                return = ['Na', 'VC', 'VC']
        Raises:
            TypeError: An error caused by wrong param type
        """
        #if not isinstance(string, str):
        #    raise TypeError("Param must be str")
        #return [pos for word, pos in pseg.cut(string)]

    def get_stat_of_part_of_speech_by_web_content(self, web_content: str) -> dict:
        """Get statistical counter of part of speech of web content by text segmentation model

        Args:
            web_content(list): A web content(HTML) in string format
        Returns:
            most_common(dict): A dict of stat of part of speech
        Raises:
            TypeError: An error caused by wrong param type
        """
        if not isinstance(web_content, str):
            raise TypeError("Param must be str")

        if not web_content:
            return {}
        sentence_list = self.chinese_sentence_filter(web_content)
        scroe_sentence = self.emotion_detector.get_score_by_sentence_list(sentence_list)
        string = self.chinese_word_filter(web_content)
        word_list, pos_sentence = self.get_word_list(string)
        scroe_sentment = self.emotion_detector.get_score_by_sentment(word_list)
        #pos_sentence = self.get_pos_list(word_list) 
        counter = self.get_stat_counter(Counter(pos_sentence))
        most_common = self.get_most_common_dict(counter)
        most_common.update(dict(counter))
        most_common.update({"scroe_sentment":scroe_sentment,"scroe_sentence":scroe_sentence})
        return most_common

    def add_word(self, company_list: list) -> None:
        """
        Add word into jieba

        Args:
            company_list(list): A list of company name
        """
        word_list = [{"批踢踢": "ORG"},{"訊連": "ORG"},{"台積電": "ORG"} ]
        for word in word_list:
            jieba.add_word(list(word.keys())[0], tag="ORG")

        for company in company_list:
            jieba.add_word(company, tag="ORG")