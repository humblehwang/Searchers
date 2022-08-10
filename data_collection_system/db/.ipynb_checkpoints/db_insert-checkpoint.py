"""
utility : 跟DB insert、update相關的function
"""
import sys
import pathlib
sys.path.append(str(pathlib.Path(__file__).parent.parent.resolve()))
sys.path.append(str(pathlib.Path(__file__).parent.parent.parent.resolve()))
import pymongo
import pandas as pd
from data_collection_system.tools import log
from data_collection_system.tools.utils import get_db_connection

logger = log.create_logger()

def insert_data(data, tartget_collection):
    db = get_db_connection()
    collection = db[tartget_collection]
    try:
        collection.insert_one(data)  
        return True
    except Exception as error:
        logger.error(f"""insert_data {tartget_collection} with {error}""")
        return False
    
def insert_data_list(data_list, tartget_collection):
    db = get_db_connection()
    collection = db[tartget_collection]
    try:
        collection.insert_many(data_list)  
        return True
    except Exception as error:
        logger.error(f"""insert_data {tartget_collection} with {error}""")
        return False
    