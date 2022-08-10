"""
utility : 跟DB insert、update相關的function
"""
from bson.objectid import ObjectId
import pymongo
import pandas as pd
import log
import utils
from utils import get_db_connection


logger = log.create_logger()
    
def get_existed_url(source, board):
    #utility: get existed url list (in DB)
    try:
        db = get_db_connection()
        db.list_collection_names()
        collection = db['article']
        query = {
            "source" : source,
            "board" : board,
        }
        data = list(collection.find(query))
        url_list = []
        for d in data:
            url_list.append(d['url'])
        return url_list
    except Exception as error:
        logger.error(f"""get_existed_url with {error}""")
        return False
    
def get_latest_existed_url(source, board):
    """
    utility: get latest existed url list (in DB) and if the latest datetime of data is not correct datetime format, we will delete it and query again
    """
    try:
        db = get_db_connection()
        db.list_collection_names()
        collection = db['article']
        query = {
            "source" : source,
            "board" : board,
        }
        while 1 :
            data = list(collection.find(query).sort([("date_time",-1)]).limit(-1))[0]
            if not data: 
                return ''
        
            if utils.check_time_format(data['date_time']):
                break
                
            collection.delete_one({"_id":ObjectId(data['_id'])})
        return data['url']
    
    except Exception as error:
        logger.error(f"""get_latest_existed_url with {error}""")
        return False
    
def get_existed_article_id(source, board):
    #utility: get existed url list (in DB)
    try:
        db = get_db_connection()
        db.list_collection_names()
        collection = db['article']
        query = {
            "source" : source,
            "board" : board,
        }
        data = list(collection.find(query))
        url_list = []
        for d in data:
            url_list.append(d['article_id'])
        return url_list
    except Exception as error:
        logger.error(f"""get_existed_article_id with {error}""")
        return False
    
def get_latest_existed_article_id(source, board):
    """
    utility: get latest existed url list (in DB) and if the latest datetime of data is not correct datetime format, we will delete it and query again
    """
    try:
        db = get_db_connection()
        db.list_collection_names()
        collection = db['article']
        query = {
            "source" : source,
            "board" : board,
        }
        while 1 :
            data = list(collection.find(query).sort([("date_time",-1)]).limit(-1))[0]
            if not data: 
                return ''
        
            if utils.check_time_format(data['date_time']):
                break
                
            collection.delete_one({"_id":ObjectId(data['_id'])})
        return data['article_id']
    
    except Exception as error:
        logger.error(f"""get_latest_existed_article_id with {error}""")
        return False
    