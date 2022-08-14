from snownlp import SnowNLP
#from opencc import OpenCC
import pandas as pd

class EmotionDetection(object):
    """
    This singleton class is used to emotion detection

    Attributes:
        sentment_dict(dict): A dict of sentment word
        ced_dir(str): The path of text ced definition file

    """
    _instance = None 
    def __new__(cls, *args, **kwargs): 
        if cls._instance is None: 
            cls._instance = super().__new__(cls) 
        return cls._instance 

    def __init__(self, ced_dir):
        self.sentment_dict = {}
        self.ced_dir = ced_dir

    def get_sentment_dict(self) -> None:
        """Get the sentment dict from excel"""
        pos_table = pd.read_excel(self.ced_dir,sheet_name='Sheet2')
        neg_table = pd.read_excel(self.ced_dir,sheet_name='Sheet3')
        pos_dict = dict(zip(list(pos_table.posword),list(pos_table.score)))
        neg_dict = dict(zip(list(neg_table.negword),map(lambda a:a*(0-1),list(neg_table.score)) ))
        self.sentment_dict = {**pos_dict,**neg_dict}

    def get_score_by_sentment(self, word_list: list) -> int:
        """Get the emotion score by given word list and
           score by sentment dict

        Args:
            word_list(list): A list of word
        Returns:
            score(int): A score of emotion

        Raises:
            TypeError: An error caused by wrong param type
        """
        if not isinstance(word_list, list):
            raise TypeError("Param must be list")
        score = 0
        for word in word_list:
            if word in self.sentment_dict.keys():
                score += self.sentment_dict[word]
        return round(score, 3)

    def get_score_by_sentence_list(self, sentence_list: list) -> int:
        """Get the emotion score by given sentence list

        Args:
            sentence_list(list): A list of Chinese sentence
        Returns:
            score(int): A score of emotion

        Raises:
            TypeError: An error caused by wrong param type
        """
        if not isinstance(sentence_list, list):
            raise TypeError("Param must be list")
        score = 0
        for sentence in sentence_list:
            if sentence:
                score += SnowNLP(sentence).sentiments
        return round(score, 3)
